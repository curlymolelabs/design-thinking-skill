"""In-memory data store for a small team SaaS app (Python, no framework)."""
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    id: int
    email: str
    name: str
    role: str = "member"          # "owner", "admin", or "member"
    team_id: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Team:
    id: int
    name: str
    plan: str = "free"            # "free" or "pro"
    seats: int = 5
    stripe_subscription_id: str | None = None

@dataclass
class Customer:
    id: int
    team_id: int
    name: str
    email: str
    phone: str
    notes: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Post:
    id: int
    author_id: int
    team_id: int
    body: str

DB = {"users": {}, "teams": {}, "customers": {}, "posts": {}}
