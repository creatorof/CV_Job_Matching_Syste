from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.auth import auth_handler
from app.database.db import get_db
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate, UserResponse, Token, UserLogin
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user information"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    
    if user_update.password is not None:
        user.hashed_password = auth_handler.get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(user)
    
    return user


