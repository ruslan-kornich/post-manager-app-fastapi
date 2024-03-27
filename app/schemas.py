from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class PostCreate(BaseModel):
    text: str


class PostResponse(BaseModel):
    id: int
    text: str
