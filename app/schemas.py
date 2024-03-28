from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=50)


class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=50)


class PostCreate(BaseModel):
    text: constr(max_length=1000)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str = None


class PostResponse(BaseModel):
    postID: int
    message: str = "Post created successfully"
