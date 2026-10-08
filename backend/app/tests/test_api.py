import pytest
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_root_and_health(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["app"] == "LifeOS"

    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_auth_and_protected_routes(client):
    # 1. Access protected route without token -> 401
    res = await client.get("/api/v1/tasks/")
    assert res.status_code == 401

    # 2. Register user
    reg_data = {
        "email": "sarah@lifeos.dev",
        "full_name": "Sarah Connor",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_data)
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert "access_token" in data
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Get profile /me
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "sarah@lifeos.dev"

    # 4. Login user
    login_data = {
        "email": "sarah@lifeos.dev",
        "password": "Password123!",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_data)
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


@pytest.mark.asyncio
async def test_tasks_crud(client):
    # Register & get auth token
    reg = await client.post("/api/v1/auth/register", json={
        "email": "alex@lifeos.dev",
        "full_name": "Alex Mercer",
        "password": "Password123!",
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create task
    task_payload = {
        "title": "Design LifeOS system architecture",
        "description": "Create modular frontend & backend specification",
        "status": "todo",
        "priority": "high",
        "due_date": str(date.today()),
        "category": "Work",
        "subtasks": [
            {"title": "Schema design", "is_completed": False, "position": 0},
            {"title": "API implementation", "is_completed": False, "position": 1},
        ]
    }
    create_res = await client.post("/api/v1/tasks/", json=task_payload, headers=headers)
    assert create_res.status_code == 201
    task_id = create_res.json()["id"]
    assert len(create_res.json()["subtasks"]) == 2

    # List tasks
    list_res = await client.get("/api/v1/tasks/", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # Update task to completed
    update_res = await client.patch(f"/api/v1/tasks/{task_id}", json={"status": "completed"}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "completed"
    assert update_res.json()["completed_at"] is not None


@pytest.mark.asyncio
async def test_habits_and_streaks(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "habit_user@lifeos.dev",
        "full_name": "James Habit",
        "password": "Password123!",
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create habit
    habit_payload = {
        "name": "Morning Meditation",
        "description": "15 minutes mindfulness",
        "frequency": "daily",
        "target_value": 15,
        "unit": "minutes",
        "color": "#6366f1",
        "icon": "smile",
        "start_date": str(date.today() - timedelta(days=5)),
    }
    create_res = await client.post("/api/v1/habits/", json=habit_payload, headers=headers)
    assert create_res.status_code == 201
    habit_id = create_res.json()["id"]

    # Toggle habit completion for today
    toggle_res = await client.post(f"/api/v1/habits/{habit_id}/toggle", headers=headers)
    assert toggle_res.status_code == 200
    assert toggle_res.json()["today_completed"] is True
    assert toggle_res.json()["current_streak"] >= 1


@pytest.mark.asyncio
async def test_goals_milestones_and_finance(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "finance_user@lifeos.dev",
        "full_name": "Oliver Twist",
        "password": "Password123!",
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create goal with milestones
    goal_payload = {
        "title": "Save $10,000 Emergency Fund",
        "category": "Finance",
        "target_value": 10000,
        "current_value": 3500,
        "unit": "$",
        "start_date": str(date.today()),
        "target_date": str(date.today() + timedelta(days=180)),
        "status": "active",
        "milestones": [
            {"title": "First $2,500 saved", "is_completed": True},
            {"title": "$5,000 milestone", "is_completed": False},
        ]
    }
    goal_res = await client.post("/api/v1/goals/", json=goal_payload, headers=headers)
    assert goal_res.status_code == 201
    assert goal_res.json()["progress_percentage"] == 50.0

    # Add income transaction
    tx_income = await client.post("/api/v1/finance/transactions", json={
        "amount": 5000,
        "type": "income",
        "category": "Other",
        "date": str(date.today()),
        "description": "Monthly Salary",
        "payment_method": "Bank Transfer",
    }, headers=headers)
    assert tx_income.status_code == 201

    # Add expense transaction
    tx_expense = await client.post("/api/v1/finance/transactions", json={
        "amount": 1200,
        "type": "expense",
        "category": "Food",
        "date": str(date.today()),
        "description": "Groceries and Dining",
        "payment_method": "Card",
    }, headers=headers)
    assert tx_expense.status_code == 201

    # Get finance summary
    fin_summary = await client.get("/api/v1/finance/summary", headers=headers)
    assert fin_summary.status_code == 200
    data = fin_summary.json()
    assert data["total_income"] == 5000.0
    assert data["total_expenses"] == 1200.0
    assert data["savings"] == 3800.0


@pytest.mark.asyncio
async def test_dashboard_consolidated_summary(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "dash_user@lifeos.dev",
        "full_name": "Tony Stark",
        "password": "Password123!",
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    dash_res = await client.get("/api/v1/dashboard/", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert "Tony Stark" in dash_data["greeting"]
    assert "productivity" in dash_data
    assert "tasks_summary" in dash_data
    assert "habits_summary" in dash_data
    assert "finance_summary" in dash_data
