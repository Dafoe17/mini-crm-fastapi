import pytest
from faker import Faker
import random
from src.enums import UserRole
from src.models import User
from src.core.security import hash_password
from tests.conftest import override_get_db

fake = Faker()

@pytest.fixture
def fake_users():
    db = next(override_get_db())
    users = []
    for i in range(20):
        user = User(
            username=fake.user_name(),
            password=hash_password("password1!"),
            role=random.choice(list(UserRole)).value
        )
        db.add(user)
        users.append(user)
    db.commit()
    yield users
    for user in users:
        db.delete(user)
    db.commit()