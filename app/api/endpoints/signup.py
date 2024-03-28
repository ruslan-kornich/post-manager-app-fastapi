from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.models.user import User as ModelUser
from app.schemas import UserCreate
from app.security import create_access_token, pwd_context

router = APIRouter()


@router.post("/signup", response_model=dict)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(ModelUser).filter(ModelUser.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    db_user = ModelUser(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
