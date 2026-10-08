from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    type: str = "expense"  # income, expense
    category: str = "Food"  # Food, Travel, Shopping, Bills, Subscriptions, Education, Entertainment, Health, Other
    date: date
    description: str = Field(..., min_length=1, max_length=255)
    payment_method: str = "Card"
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[str] = None
    category: Optional[str] = None
    date: Optional[date] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    category: str
    monthly_limit: float = Field(..., gt=0)
    month_year: str = Field(..., pattern=r"^\d{4}-\d{2}$")  # YYYY-MM


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    category: Optional[str] = None
    monthly_limit: Optional[float] = None
    month_year: Optional[str] = None


class BudgetResponse(BudgetBase):
    id: str
    user_id: str
    spent_amount: float = 0.0
    remaining_amount: float = 0.0
    percentage_used: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    billing_frequency: str = "monthly"  # monthly, quarterly, yearly
    next_billing_date: date
    category: str = "Subscriptions"
    payment_method: str = "Card"
    is_active: bool = True


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    billing_frequency: Optional[str] = None
    next_billing_date: Optional[date] = None
    category: Optional[str] = None
    payment_method: Optional[str] = None
    is_active: Optional[bool] = None


class SubscriptionResponse(SubscriptionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FinanceSummaryResponse(BaseModel):
    total_income: float = 0.0
    total_expenses: float = 0.0
    savings: float = 0.0
    savings_rate: float = 0.0
    category_breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    monthly_trend: List[Dict[str, Any]] = Field(default_factory=list)
    recent_transactions: List[TransactionResponse] = Field(default_factory=list)
    active_subscriptions_monthly_cost: float = 0.0
    active_subscriptions_yearly_cost: float = 0.0
