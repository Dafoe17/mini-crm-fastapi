import pytest
from tests.fixtures.fake_tasks import fake_task

@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.put
def test_update_task_admin(client, admin_auth_headers, test_admin, fake_task):
    updated_task = {
        "title": "Updated_title",
        "description": "",
        "due_date": None,
        "status": "todo",
        "user_name": test_admin.username
    }

    response = client.put(f"/tasks/update?title={fake_task.title}", 
                            headers=admin_auth_headers, json=updated_task)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "changed"
    assert data["tasks"]["title"] == "Updated_title"

@pytest.mark.tasks_api
@pytest.mark.non_admin
@pytest.mark.put
def test_update_task_non_admin(client, user_auth_headers, test_user, fake_task):
    updated_task = {
        "title": "Updated_title",
        "description": "",
        "due_date": None,
        "status": "todo",
        "user_name": test_user.username
    }

    response = client.put(f"/tasks/update?title={fake_task.title}", 
                            headers=user_auth_headers, json=updated_task)
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.put
def test_update_task_invalid_title(client, admin_auth_headers, test_admin, fake_task):
    updated_task = {
        "title": "N",
        "description": "",
        "due_date": None,
        "status": "todo",
        "user_name": test_admin.username
    }

    response = client.put(f"/tasks/update?title={fake_task.title}", 
                            headers=admin_auth_headers, json=updated_task)
    assert response.status_code == 400
    assert 'String should have at least 2 characters' in response.text

@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.put
def test_update_task_invalid_status(client, admin_auth_headers, test_admin, fake_task):
    updated_task = {
        "title": "Updated_title",
        "description": "",
        "due_date": None,
        "status": "idk",
        "user_name": test_admin.username
    }

    response = client.put(f"/tasks/update?title={fake_task.title}", 
                            headers=admin_auth_headers, json=updated_task)
    assert response.status_code == 400
    assert 'Input should be' in response.text

@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.put
def test_update_task_not_exists(client, admin_auth_headers, test_admin):
    updated_task = {
        "title": "Updated_title",
        "description": "",
        "due_date": None,
        "status": "todo",
        "user_name": test_admin.username
    }

    response = client.put(f"/tasks/update?title=anytitle", 
                            headers=admin_auth_headers, json=updated_task)
    assert response.status_code == 404
    assert 'Task not found' in response.text
