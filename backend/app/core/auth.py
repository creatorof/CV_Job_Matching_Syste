from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from hashlib import sha256
from fastapi import HTTPException, status
from app.core.config import settings
import logging

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

class AuthHandler:
    def verify_password(self, plain_password: str, stored_hash: str) -> bool:
        hashed_password = self.get_password_hash(plain_password)
        return hashed_password == stored_hash

    def get_password_hash(self, password: str) -> str:
        hashed_password = sha256(password.encode('utf-8')).hexdigest()
        return hashed_password
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            logging.error(f"JWT decode failed: {str(e)}, Token: {token[:50]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

auth_handler = AuthHandler()