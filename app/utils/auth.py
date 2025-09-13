from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from app.schemas.auth import TokenData
from fastapi.security import OAuth2PasswordBearer
from app.models import UserModel
from sqlalchemy.orm import Session
import os
from app.config.oauth2 import oauth2_secret_key, oauth2_algorithm, oauth2_access_token_expiry
from app.config import database


def hash_password(pwd: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_pwd = pwd_context.hash(pwd)
    return hashed_pwd


def verify_password(plain_pwd, hashed_pwd):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_pwd, hashed_pwd)


SECRET_KEY = oauth2_secret_key
ALGORITHM = oauth2_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = oauth2_access_token_expiry
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Utility function to create JWT access token
def create_access_token(data: dict):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + access_token_expires
    data_to_encode = {
        "exp": expire,
        "sub": data["user_id"]
    }
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Utility function to create refresh token
def create_refresh_token(data: dict, expires_minutes: int = 60 * 24 * 7):
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    data_to_encode = {
        "exp": expire,
        "sub": data["user_id"]
    }
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire


# Utility function to verify refresh token
def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid refresh token",
                                headers={"WWW-Authenticate": "Bearer"})
        return user_id
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid refresh token",
                            headers={"WWW-Authenticate": "Bearer"})


# Utility function to decode and verify JWT token
# Raises credentials_exception if token is invalid
def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid credentials1",
                                headers={"WWW-Authenticate": "Bearer"})
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials2",
                            headers={"WWW-Authenticate": "Bearer"})
    return token_data


# Dependency to get current user based on JWT token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    user_id = verify_access_token(token)
    user = db.query(UserModel).filter(UserModel.id == int(user_id.user_id)).first()
    return user


# Utility function to create email verification token
def create_email_verification_token():
    v_token = os.urandom(64).hex()
    v_expiry = datetime.now(timezone.utc) + timedelta(hours=24)  # Token valid for 24 hours
    return v_token, v_expiry
