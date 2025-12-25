from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import time

from app.core.auth import auth_handler
from app.database.db import get_db
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate, UserResponse, Token, UserLogin
from app.dependencies import get_current_active_user
from app.utils.logging import create_log


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new User."""
    start_time = time.perf_counter()
    try:
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        
        hashed_password = auth_handler.get_password_hash(user.password)

        new_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role="user",
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        total_time = time.perf_counter() - start_time
        create_log(
            db=db,
            log_name="user_register",
            log_type="PERF",
            function_name="register",
            time_taken=total_time
        )
        return new_user
    except Exception as e:
        create_log(
            db=db,
            log_name="user_register_failed",
            log_type="ERROR",
            function_name="register",
            description=e.detail
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        total_time = time.perf_counter() - start_time
        create_log(
            db=db,
            log_name="user_register",
            log_type="PERF",
            function_name="register",
            time_taken=total_time
        )        

@router.post("/login", response_model=Token)
async def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Login User and return JWT token"""
    start_time = time.perf_counter()

    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        
        if not db_user or not auth_handler.verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
        if not db_user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
        
        access_token = auth_handler.create_access_token(
            data={"sub": db_user.username, "role": db_user.role},
            expires_delta=timedelta(minutes=60*24)
        )
        
        token_response = Token(
            access_token=access_token,
            token_type="bearer",
            user=db_user
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=60*60*24,
            samesite="lax"
        )
        
        return token_response
    except Exception as e:
        create_log(
            db=db,
            log_name="user_login_failed",
            log_type="ERROR",
            function_name="login",
            description=e.detail
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    finally:
        total_time = time.perf_counter() - start_time
        create_log(
            db=db,
            log_name="user_login",
            log_type="PERF",
            function_name="login",
            time_taken=total_time
        )

@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Logout the user"""
    response.delete_cookie("access_token")

    create_log(
        db=db,
        log_name="user_logout",
        log_type="INFO",
        function_name="logout",
        description=f"User {current_user.username} logged out"
    )

    return {"message": "Successfully logged out"}
