import pytest
from tests.fixtures.fake_tasks import fake_task

@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.post
def test_add_task_admin(client, admin_auth_headers, test_admin):
    new_task = {
        "title": "New_title",
        "description": "",
        "due_date": None,
        "status": "todo",
        "user_name": test_admin.username
    }

    response = client.post(f"/tasks/add", 
                            headers=admin_auth_headers, json=new_task)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "created"
    assert data["tasks"]["title"] == "New_title"

@pytest.mark.tasks_api
@pytest.mark.non_admin
@pytest.mark.post
def test_add_task_non_admin(client, user_auth_headers, test_user):
    new_task = {
        "title": "New_title",
        "description": "",
        "due_date": None,
        "status": "todo",
        "user_name": test_user.username
    }

    response = client.post(f"/tasks/add", 
                            headers=user_auth_headers, json=new_task)
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.post
def test_add_task_invalid_title(client, admin_auth_headers, test_admin):
    new_task = {
        "title": "N",
        "description": "",
        "due_date": None,
        "status": "todo",
        "user_name": test_admin.username
    }

    response = client.post(f"/tasks/add", 
                            headers=admin_auth_headers, json=new_task)
    assert response.status_code == 400
    assert 'String should have at least 2 characters' in response.text

@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.post
def test_add_task_invalid_status(client, admin_auth_headers, test_admin):
    new_task = {
        "title": "New_title",
        "description": "",
        "due_date": None,
        "status": "idk",
        "user_name": test_admin.username
    }

    response = client.post(f"/tasks/add", 
                            headers=admin_auth_headers, json=new_task)
    assert response.status_code == 400
    assert 'Input should be' in response.text

@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.post
def test_add_task_already_exists(client, admin_auth_headers, test_admin, fake_task):
    new_task = {
        "title": fake_task.title,
        "description": "",
        "due_date": None,
        "status": "todo",
        "user_name": test_admin.username
    }

    response = client.post(f"/tasks/add", 
                            headers=admin_auth_headers, json=new_task)
    assert response.status_code == 409
    assert 'Task already exists' in response.text
