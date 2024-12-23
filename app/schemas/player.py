from pydantic import BaseModel
from datetime import date

class PlayerBase(BaseModel):
    username: str
    name: str
    surname: str | None = None
    gender: str | None = None
    b_date: date | None = None
    age: int | None = None
    address: str | None = None
    email: str | None = None
    password: str
    icon_id: int | None = None

class Login(BaseModel):
    username: str
    password: str

class PlayerOut(BaseModel):
    username: str
    name: str
    surname: str | None = None
    gender: str | None = None
    b_date: date | None = None
    age: int | None = None
    address: str | None = None
    email: str | None = None
    icon_id: int | None = None


    class Config:
        orm_mode = True