# app/schemas/achievement.py
from pydantic import BaseModel
from typing import Optional

class AchievementBase(BaseModel):
    name: str
    description: str

class AchievementOut(AchievementBase):
    achieve_id: int

    class Config:
        orm_mode = True

class AchieveRecordBase(BaseModel):
    username: str
    achieve_id: int

    class Config:
        orm_mode = True

