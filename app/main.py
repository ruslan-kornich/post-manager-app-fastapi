from fastapi.security import OAuth2PasswordBearer
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from typing import List
from models import User, Post
from schemas import UserCreate, UserLogin, PostCreate, Token, PostResponse
from security import pwd_context, create_access_token
from database import get_db
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session

app = FastAPI()

# Dependency for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


@app.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/addPost", response_model=PostResponse)
async def add_post(
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if len(post.text.encode("utf-8")) > 1024 * 1024:  # 1 MB
        raise HTTPException(status_code=400, detail="Payload too large")

    db_post = Post(text=post.text, user_id=current_user.email)
    db.add(db_post)
    db.commit()

    return PostResponse(postID=db_post.id, message="Post created successfully")


@app.get("/getPosts", response_model=List[PostResponse])
async def get_posts(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    posts = db.query(Post).filter(Post.user_id == current_user.email).all()
    return [{"postID": post.id, "message": post.text} for post in posts]


@app.delete("/deletePost/{postID}", response_model=dict)
async def delete_post(
    postID: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_post = (
        db.query(Post)
        .filter(Post.id == postID, Post.user_id == current_user.email)
        .first()
    )
    if db_post:
        db.delete(db_post)
        db.commit()
        return {"message": "Post deleted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
