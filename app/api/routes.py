from fastapi import APIRouter
from app.api.endpoints import signup, login, add_post, get_posts, delete_post

router = APIRouter()

router.include_router(signup.router, tags=["user"])
router.include_router(login.router, tags=["user"])
router.include_router(add_post.router, tags=["post"])
router.include_router(get_posts.router, tags=["post"])
router.include_router(delete_post.router, tags=["post"])
