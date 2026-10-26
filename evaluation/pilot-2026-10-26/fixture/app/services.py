"""Business logic. Request handlers in app/api.py call these functions."""
from app.models import DB, User, Team, Customer, Post

def get_user(user_id: int) -> User:
    return DB["users"][user_id]

def team_members(team_id: int) -> list[User]:
    return [u for u in DB["users"].values() if u.team_id == team_id]

def list_customers(team_id: int) -> list[Customer]:
    return [c for c in DB["customers"].values() if c.team_id == team_id]

def send_email(to: str, subject: str, body: str) -> None:
    print(f"EMAIL to={to} subject={subject}")

def cancel_subscription(subscription_id: str) -> None:
    print(f"STRIPE cancel {subscription_id}")
