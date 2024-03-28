import os

from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base


from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///" + os.path.join(os.getcwd(), "app/database/test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
