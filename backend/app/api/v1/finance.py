from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from typing import List, Optional, Dict, Any
from datetime import date, datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.finance import Transaction, Budget, Subscription
from app.schemas.finance import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    BudgetCreate, BudgetUpdate, BudgetResponse,
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse,
    FinanceSummaryResponse
)

router = APIRouter()


# --- Transactions ---

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    type: Optional[str] = Query(None, description="income or expense"),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(limit)
    )
    if type:
        stmt = stmt.where(Transaction.type == type)
    if category:
        stmt = stmt.where(Transaction.category == category)
    if start_date:
        stmt = stmt.where(Transaction.date >= start_date)
    if end_date:
        stmt = stmt.where(Transaction.date <= end_date)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    trans_in: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    transaction = Transaction(**trans_in.model_dump(), user_id=current_user.id)
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


@router.patch("/transactions/{trans_id}", response_model=TransactionResponse)
async def update_transaction(
    trans_id: str,
    trans_in: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Transaction).where(and_(Transaction.id == trans_id, Transaction.user_id == current_user.id))
    transaction = (await db.execute(stmt)).scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    update_data = trans_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    await db.commit()
    await db.refresh(transaction)
    return transaction


@router.delete("/transactions/{trans_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    trans_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Transaction).where(and_(Transaction.id == trans_id, Transaction.user_id == current_user.id))
    transaction = (await db.execute(stmt)).scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    await db.delete(transaction)
    await db.commit()
    return None


# --- Budgets ---

@router.get("/budgets", response_model=List[BudgetResponse])
async def get_budgets(
    month_year: Optional[str] = Query(None, description="Format: YYYY-MM"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    target_month = month_year or date.today().strftime("%Y-%m")
    stmt = select(Budget).where(and_(Budget.user_id == current_user.id, Budget.month_year == target_month))
    result = await db.execute(stmt)
    budgets = result.scalars().all()

    # Get expense totals by category for target month
    # Assuming date starts with 'YYYY-MM'
    stmt_tx = select(
        Transaction.category,
        func.sum(Transaction.amount).label("spent")
    ).where(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.type == "expense"
        )
    ).group_by(Transaction.category)
    
    tx_res = await db.execute(stmt_tx)
    # We filter by matching month in python or query
    # Fetch user transactions for this month to compute exact category spent:
    stmt_month_tx = select(Transaction).where(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.type == "expense"
        )
    )
    month_txs = (await db.execute(stmt_month_tx)).scalars().all()
    spent_by_category = {}
    for tx in month_txs:
        if tx.date.strftime("%Y-%m") == target_month:
            spent_by_category[tx.category] = spent_by_category.get(tx.category, 0.0) + tx.amount

    budget_responses = []
    for b in budgets:
        spent = round(spent_by_category.get(b.category, 0.0), 2)
        remaining = round(b.monthly_limit - spent, 2)
        pct = round((spent / b.monthly_limit) * 100, 1) if b.monthly_limit > 0 else 0.0
        budget_responses.append(BudgetResponse(
            id=b.id,
            user_id=b.user_id,
            category=b.category,
            monthly_limit=b.monthly_limit,
            month_year=b.month_year,
            spent_amount=spent,
            remaining_amount=remaining,
            percentage_used=pct,
            created_at=b.created_at,
            updated_at=b.updated_at,
        ))

    return budget_responses


@router.post("/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_in: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if budget for this category and month exists
    stmt = select(Budget).where(
        and_(
            Budget.user_id == current_user.id,
            Budget.category == budget_in.category,
            Budget.month_year == budget_in.month_year
        )
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        existing.monthly_limit = budget_in.monthly_limit
        await db.commit()
        await db.refresh(existing)
        b = existing
    else:
        b = Budget(**budget_in.model_dump(), user_id=current_user.id)
        db.add(b)
        await db.commit()
        await db.refresh(b)

    return BudgetResponse(
        id=b.id,
        user_id=b.user_id,
        category=b.category,
        monthly_limit=b.monthly_limit,
        month_year=b.month_year,
        spent_amount=0.0,
        remaining_amount=b.monthly_limit,
        percentage_used=0.0,
        created_at=b.created_at,
        updated_at=b.updated_at,
    )


@router.delete("/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Budget).where(and_(Budget.id == budget_id, Budget.user_id == current_user.id))
    budget = (await db.execute(stmt)).scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    await db.delete(budget)
    await db.commit()
    return None


# --- Subscriptions ---

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Subscription).where(Subscription.user_id == current_user.id).order_by(Subscription.next_billing_date.asc())
    if active_only:
        stmt = stmt.where(Subscription.is_active == True)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    sub_in: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    subscription = Subscription(**sub_in.model_dump(), user_id=current_user.id)
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    return subscription


@router.patch("/subscriptions/{sub_id}", response_model=SubscriptionResponse)
async def update_subscription(
    sub_id: str,
    sub_in: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Subscription).where(and_(Subscription.id == sub_id, Subscription.user_id == current_user.id))
    sub = (await db.execute(stmt)).scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    update_data = sub_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sub, field, value)

    await db.commit()
    await db.refresh(sub)
    return sub


@router.delete("/subscriptions/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    sub_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Subscription).where(and_(Subscription.id == sub_id, Subscription.user_id == current_user.id))
    sub = (await db.execute(stmt)).scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    await db.delete(sub)
    await db.commit()
    return None


# --- Finance Summary ---

@router.get("/summary", response_model=FinanceSummaryResponse)
async def get_finance_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch all transactions
    stmt_tx = select(Transaction).where(Transaction.user_id == current_user.id).order_by(Transaction.date.desc())
    transactions = (await db.execute(stmt_tx)).scalars().all()

    current_month_str = date.today().strftime("%Y-%m")
    total_income = 0.0
    total_expenses = 0.0
    category_expenses: Dict[str, float] = {}
    monthly_map: Dict[str, Dict[str, float]] = {}

    for tx in transactions:
        m_str = tx.date.strftime("%Y-%m")
        if m_str not in monthly_map:
            monthly_map[m_str] = {"income": 0.0, "expenses": 0.0}

        if tx.type == "income":
            if m_str == current_month_str:
                total_income += tx.amount
            monthly_map[m_str]["income"] += tx.amount
        elif tx.type == "expense":
            if m_str == current_month_str:
                total_expenses += tx.amount
                category_expenses[tx.category] = category_expenses.get(tx.category, 0.0) + tx.amount
            monthly_map[m_str]["expenses"] += tx.amount

    savings = round(total_income - total_expenses, 2)
    savings_rate = round((savings / total_income * 100), 1) if total_income > 0 else 0.0

    category_breakdown = [
        {"category": cat, "amount": round(amt, 2), "percentage": round((amt / total_expenses * 100), 1) if total_expenses > 0 else 0.0}
        for cat, amt in sorted(category_expenses.items(), key=lambda x: x[1], reverse=True)
    ]

    # Last 6 months trend sorted chronologically
    sorted_months = sorted(list(monthly_map.keys()))[-6:]
    monthly_trend = [
        {
            "month": m,
            "income": round(monthly_map[m]["income"], 2),
            "expenses": round(monthly_map[m]["expenses"], 2),
            "savings": round(monthly_map[m]["income"] - monthly_map[m]["expenses"], 2)
        }
        for m in sorted_months
    ]

    # Subscriptions cost
    stmt_sub = select(Subscription).where(and_(Subscription.user_id == current_user.id, Subscription.is_active == True))
    subs = (await db.execute(stmt_sub)).scalars().all()
    monthly_sub_cost = 0.0
    yearly_sub_cost = 0.0
    for s in subs:
        if s.billing_frequency == "monthly":
            monthly_sub_cost += s.amount
            yearly_sub_cost += s.amount * 12
        elif s.billing_frequency == "quarterly":
            monthly_sub_cost += s.amount / 3
            yearly_sub_cost += s.amount * 4
        elif s.billing_frequency == "yearly":
            monthly_sub_cost += s.amount / 12
            yearly_sub_cost += s.amount

    return FinanceSummaryResponse(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        savings=savings,
        savings_rate=savings_rate,
        category_breakdown=category_breakdown,
        monthly_trend=monthly_trend,
        recent_transactions=transactions[:5],
        active_subscriptions_monthly_cost=round(monthly_sub_cost, 2),
        active_subscriptions_yearly_cost=round(yearly_sub_cost, 2),
    )
