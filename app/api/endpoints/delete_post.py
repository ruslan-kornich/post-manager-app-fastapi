from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.services import post_service
from app.security import get_current_user
from app.core.models.user import User

router = APIRouter()


@router.delete("/deletePost/{postID}", response_model=dict)
async def delete_post(
    postID: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = post_service.delete_post(db, postID, current_user.email)
    if deleted:
        return {"message": "Post deleted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
