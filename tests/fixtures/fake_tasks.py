import pytest
from faker import Faker
import random
from src.enums import TaskStatus
from src.models import Task
from tests.conftest import override_get_db

fake = Faker()

@pytest.fixture
def fake_tasks():
    db = next(override_get_db())
    tasks = []
    for _ in range(20):
        task = Task(
            title=fake.text(max_nb_chars=50),
            description=fake.text(max_nb_chars=50),
            due_date=None,
            status=random.choice(list(TaskStatus)).value
        )

        db.add(task)
        tasks.append(task)
    db.commit()
    yield tasks
    for task in tasks:
        db.delete(task)
    db.commit()

@pytest.fixture
def fake_task():
    db = next(override_get_db())
    task = Task(
            title=fake.text(max_nb_chars=50),
            description=fake.text(max_nb_chars=50),
            due_date=None,
            status=random.choice(list(TaskStatus)).value
    )
    db.add(task)
    db.commit()
    yield task
    db.delete(task)
    db.commit()

@pytest.fixture
def fake_tasks_for_delete():
    db = next(override_get_db())
    tasks = []
    for _ in range(20):
        task = Task(
            title=fake.text(max_nb_chars=50),
            description=fake.text(max_nb_chars=50),
            due_date="2024-11-10",
            status="done"
        )

        db.add(task)
        tasks.append(task)

    db.commit()
    try:
        yield tasks
    finally:
        db.rollback()
        db.close()
        
@pytest.fixture
def fake_task_for_delete():
    db = next(override_get_db())
    task = Task(
            title=fake.text(max_nb_chars=50),
            description=fake.text(max_nb_chars=50),
            due_date=None,
            status=random.choice(list(TaskStatus)).value
    )
    db.add(task)
    db.commit()
    try:
        yield task
    finally:
        db.rollback()
        db.close()

