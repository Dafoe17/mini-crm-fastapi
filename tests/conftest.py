import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import Base
from src.api.dependencies import get_db
from src.models import User
from src.core.security import hash_password
from src.core.config import settings


engine_test = create_engine(settings.TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(bind=engine_test, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_admin():
    db = next(override_get_db())
    admin = User(
        username="testadmin",
        password=hash_password("testp!1sword"),
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    yield admin
    db.delete(admin)
    db.commit()


@pytest.fixture
def test_manager():
    db = next(override_get_db())
    manager = User(
        username="testmanager",
        password=hash_password("testp!1sword"),
        role="manager"
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    yield manager
    db.delete(manager)
    db.commit()


@pytest.fixture
def test_user():
    db = next(override_get_db())
    user = User(
        username="testuser",
        password=hash_password("testp!1sword"),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()

@pytest.fixture
def admin_auth_headers(client, test_admin):
    response = client.post(
        "/auth/login",
        data={"username": test_admin.username, "password": "testp!1sword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def manager_auth_headers(client, test_manager):
    response = client.post(
        "/auth/login",
        data={"username": test_manager.username, "password": "testp!1sword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def user_auth_headers(client, test_user):
    response = client.post(
        "/auth/login",
        data={"username": test_user.username, "password": "testp!1sword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

