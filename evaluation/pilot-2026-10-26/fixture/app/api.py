"""HTTP-style handlers. Each takes the current user and returns a dict."""
from app import services

def me(current_user):
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role}

def customers(current_user):
    return {"customers": [c.__dict__ for c in services.list_customers(current_user.team_id)]}
