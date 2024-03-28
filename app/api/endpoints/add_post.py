from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.models.post import Post as ModelPost
from app.core.models.user import User as ModelUser
from app.schemas import PostCreate
from app.security import get_current_user

router = APIRouter()


@router.post("/addPost", response_model=dict)
async def add_post(
    post: PostCreate,
    current_user: ModelUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if len(post.text.encode("utf-8")) > 1024 * 1024:  # 1 MB
        raise HTTPException(status_code=400, detail="Payload too large")

    db_post = ModelPost(text=post.text, user_id=current_user.email)
    db.add(db_post)
    db.commit()

    return {"postID": db_post.id, "message": "Post created successfully"}
