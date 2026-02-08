from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Profile:
    name: str
    email: str


@dataclass(frozen=True)
class User:
    id: str
    profile: Profile
    password: str
    memo: str | None
    created_at: datetime
    updated_at: datetime
