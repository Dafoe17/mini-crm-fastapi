import pytest
from faker import Faker
from src.models import Client
from src.core.security import hash_password
from tests.conftest import override_get_db

fake = Faker("ru_RU")

@pytest.fixture
def fake_clients():
    db = next(override_get_db())
    clients = []
    for _ in range(20):
        client = Client(
            name=fake.name()[:50],
            email=fake.ascii_free_email(),
            phone=fake.phone_number(),
            notes=fake.text()
        )
        db.add(client)
        clients.append(client)
    db.commit()

    for c in clients:
        db.refresh(c)

    yield clients
    for client in clients:
        db_client = db.get(Client, client.id)
        if db_client:
            db.delete(db_client)
    db.commit()

@pytest.fixture
def fake_client_with_no_user():
    db = next(override_get_db())
    client = Client(
        name=fake.name()[:50],
        email=fake.ascii_free_email(),
        phone=fake.phone_number(),
        notes=fake.text()
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    yield client

    db_client = db.get(Client, client.id)
    if db_client is None:
        return 
    db.delete(db_client)
    db.commit()

@pytest.fixture
def fake_client_for_delete():
    db = next(override_get_db())
    client = Client(
        name=fake.name()[:50],
        email=fake.ascii_free_email(),
        phone=fake.phone_number(),
        notes=fake.text()
    )
    db.add(client)
    db.commit()
    db.refresh(client)

    try:
        yield client
    finally:
        db.rollback()
        db.close()     