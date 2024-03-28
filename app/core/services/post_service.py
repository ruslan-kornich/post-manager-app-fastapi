from sqlalchemy.orm import Session
from app.core.models.post import Post
from app.schemas import PostCreate


def create_post(db: Session, post: PostCreate, user_email: str):
    db_post = Post(text=post.text, user_id=user_email)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_posts_by_user(db: Session, user_email: str):
    return db.query(Post).filter(Post.user_id == user_email).all()


def delete_post(db: Session, post_id: int, user_email: str):
    db_post = (
        db.query(Post).filter(Post.id == post_id, Post.user_id == user_email).first()
    )
    if db_post:
        db.delete(db_post)
        db.commit()
        return True
    return False
