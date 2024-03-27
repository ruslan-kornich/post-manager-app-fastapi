from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from typing import List
from models import User

from database import get_db
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Dependency for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Generate JWT token
def create_access_token(data: dict, expires_delta: int = 30):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "secret_key", algorithm="HS256")
    return encoded_jwt


# Dependency to get current user from token
def get_current_user(
        token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode(token, "secret_key", algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
