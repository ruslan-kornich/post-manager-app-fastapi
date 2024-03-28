import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.schemas import UserCreate, UserLogin
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app=app)


@pytest.fixture
def test_user():
    user = UserCreate(email="test@example.com", password="testpassword")
    return user


@pytest.fixture
def access_token(test_user):
    # Signup
    response = client.post("/signup", json=test_user.model_dump())
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Login
    login_data = UserLogin(email=test_user.email, password=test_user.password)
    response = client.post("/login", json=login_data.model_dump())
    assert response.status_code == 200
    assert "access_token" in response.json()

    return response.json()["access_token"]


@pytest.fixture(autouse=True)
def cleanup_database():
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_signup_and_login(test_user):
    # Signup
    response = client.post("/signup", json=test_user.model_dump())
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Login
    login_data = UserLogin(email=test_user.email, password=test_user.password)
    response = client.post("/login", json=login_data.model_dump())
    assert response.status_code == 200
    assert "access_token" in response.json()

    assert response.json()["access_token"]


def test_add_post(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    post_data = {"text": "Test post"}
    response = client.post("/addPost", json=post_data, headers=headers)
    assert response.status_code == 200
    assert "postID" in response.json()


def test_get_posts(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/getPosts", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_post(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    post_data = {"text": "Test post"}
    response = client.post("/addPost", json=post_data, headers=headers)
    post_id = response.json()["postID"]
    response = client.delete(f"/deletePost/{post_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Post deleted"


def test_invalid_credentials():
    login_data = UserLogin(email="test@example.com", password="wrongpassword")
    response = client.post("/login", json=login_data.model_dump())
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
