import pytest
from faker import Faker
import random
from src.enums import DealStatus
from src.models import Deal
from tests.conftest import override_get_db
from tests.fixtures.fake_clients import fake_client_with_no_user

fake = Faker()

@pytest.fixture
def fake_deals(fake_client_with_no_user):
    db = next(override_get_db())
    deals = []
    for _ in range(20):
        deal = Deal(
            title=fake.text(max_nb_chars=50),
            status=random.choice(list(DealStatus)).value,
            value=random.randint(0,100000000),
            closed_at=None,
            client_id=fake_client_with_no_user.id
        )

        db.add(deal)
        deals.append(deal)
    db.commit()
    yield deals
    for deal in deals:
        db.delete(deal)
    db.commit()

@pytest.fixture
def fake_deal(fake_client_with_no_user):
    db = next(override_get_db())
    deal = Deal(
        title=fake.text(max_nb_chars=50),
        status=random.choice(list(DealStatus)).value,
        value=random.randint(0,100000000),
        closed_at=None,
        client_id=fake_client_with_no_user.id
    )
    db.add(deal)
    db.commit()
    yield deal
    db.delete(deal)
    db.commit()

@pytest.fixture
def fake_deals_for_delete(fake_client_with_no_user):
    db = next(override_get_db())
    deals = []
    for _ in range(20):
        deal = Deal(
            title=fake.text(max_nb_chars=50),
            status=random.choice(list(DealStatus)).value,
            value=random.randint(0,100000000),
            closed_at=None,
            client_id=fake_client_with_no_user.id
        )

        db.add(deal)
        deals.append(deal)

    db.commit()
    try:
        yield deals
    finally:
        db.rollback()
        db.close()
        
@pytest.fixture
def fake_deal_for_delete(fake_client_with_no_user):
    db = next(override_get_db())
    deal = Deal(
        title=fake.text(max_nb_chars=50),
        status=random.choice(list(DealStatus)).value,
        value=random.randint(0,100000000),
        closed_at=None,
        client_id=fake_client_with_no_user.id
    )
    db.add(deal)
    db.commit()
    try:
        yield deal
    finally:
        db.rollback()
        db.close()