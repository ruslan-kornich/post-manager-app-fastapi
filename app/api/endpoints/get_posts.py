from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.core.models.post import Post as ModelPost
from app.schemas import PostResponse as SchemaPost
from app.security import get_current_user
from cachetools import LRUCache

router = APIRouter()

# Initialize Cache
cache = LRUCache(maxsize=1000)


@router.get("/getPosts", response_model=List[SchemaPost])
async def get_posts(
    current_user: ModelPost = Depends(get_current_user), db: Session = Depends(get_db)
):
    posts = db.query(ModelPost).filter(ModelPost.user_id == current_user.email).all()
    cached_data = cache.get(current_user.email)
    if cached_data:
        return cached_data

    response_data = [{"postID": post.id, "message": post.text} for post in posts]
    cache[current_user.email] = response_data
    cache.pop(current_user.email, None)  # expire the cache after 5 minutes

    return response_data
