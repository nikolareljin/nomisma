"""
Authentication utilities for JWT token handling and password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os

from .database import get_db
from . import models

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
DEFAULT_USERNAME = os.getenv("DEFAULT_USERNAME", "local")
DEFAULT_EMAIL = os.getenv("DEFAULT_EMAIL", "local@nomisma.local")
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "local")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def _get_user_from_token(token: str, db: Session) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


def _get_or_create_default_user(db: Session) -> models.User:
    user = db.query(models.User).filter(models.User.username == DEFAULT_USERNAME).first()
    if user:
        if not user.is_active:
            user.is_active = True
            db.commit()
            db.refresh(user)
        return user

    user_by_email = db.query(models.User).filter(models.User.email == DEFAULT_EMAIL).first()
    if user_by_email:
        if not user_by_email.is_active:
            user_by_email.is_active = True
            db.commit()
            db.refresh(user_by_email)
        return user_by_email

    hashed_password = get_password_hash(DEFAULT_PASSWORD)
    user = models.User(
        username=DEFAULT_USERNAME,
        email=DEFAULT_EMAIL,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency to get the current authenticated user from JWT token.
    Raises HTTPException if token is invalid or user not found.
    """
    return _get_user_from_token(token, db)


def get_request_user(
    token: Optional[str] = Depends(optional_oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency to get the current user if authenticated, or a local default user.
    """
    if token:
        return _get_user_from_token(token, db)

    return _get_or_create_default_user(db)


def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """Dependency to ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
