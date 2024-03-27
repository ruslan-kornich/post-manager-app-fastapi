from typing import List
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from cachetools import LRUCache
from models import User, Post
from schemas import UserCreate, UserLogin, PostCreate, Token, PostResponse
from security import pwd_context, create_access_token, get_current_user
from database import get_db

app = FastAPI()

# Initialize Cache
cache = LRUCache(maxsize=1000)


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
    db_post = Post(text=post.text, user_id=current_user.email)
    db.add(db_post)
    db.commit()

    return PostResponse(postID=db_post.id, message="Post created successfully")


@app.get("/getPosts", response_model=List[PostResponse])
async def get_posts(
        current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    posts = db.query(Post).filter(Post.user_id == current_user.email).all()
    cached_data = cache.get(current_user.email)
    if cached_data:
        return cached_data

    response_data = [{"postID": post.id, "message": post.text} for post in posts]
    cache[current_user.email] = response_data
    cache.expire(current_user.email, time=300)  # expire after 5 minutes

    return response_data


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
