from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session


app = FastAPI()

@app.get("/")
async def check():
    return "Hello"

# models.Base.metadata.create_all(bind=engine)

# class UserBase(BaseModel):
# 	username: str

# def get_db():
# 	db= SessionLocal()
# 	try: 
# 		yield db
# 	finally:
# 		db.close()

# db_dependency = Annotated[Session, Depends(get_db)]

# @app.post('/users/create', status_code=status.HTTP_201_CREATED)
# async def create_user(user: UserBase, db: db_dependency):
#     db_user = models.User(**user.dict())
#     db.add(db_user)
#     db.commit()
#     return db_user

# @app.get('/users/get', status_code=status.HTTP_200_OK)
# async def get_user(db: db_dependency):
#     users = db.query(models.User).all()
#     return users

# @app.delete('/users/delete/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(user_id: int, db: db_dependency):
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     db.delete(user)
#     db.commit()
#     return {"message": "User deleted successfully"}

# @app.put('/users/update/{user_id}', status_code=status.HTTP_200_OK)
# async def update_user(user_id: int, user_update: UserBase, db: db_dependency):
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     user.username = user_update.username
#     db.commit()
#     db.refresh(user)
#     return user



