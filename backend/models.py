from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime
import uuid

class CategoryEnum(str, Enum):
    GOOD = "GOOD"
    BAD = "BAD"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    total_cookies: int = 0
    streak_count: int = 0

class Habit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    category: CategoryEnum
    target_daily: int

class LogEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    habit_id: str
    timestamp: datetime
    trigger_type: str
    mood_tag: Optional[str] = None
    lat_long: Optional[str] = None
