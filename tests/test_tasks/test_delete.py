import pytest
from tests.fixtures.fake_tasks import fake_task_for_delete, fake_tasks_for_delete

@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.delete
def test_delete_task_admin(client, admin_auth_headers, fake_task_for_delete):

    response = client.delete(f"/tasks/delete?title={fake_task_for_delete.title}", 
                             headers=admin_auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "deleted"
    assert data["tasks"]["title"] == fake_task_for_delete.title

@pytest.mark.tasks_api
@pytest.mark.non_admin
@pytest.mark.delete
def test_delete_task_non_admin(client, user_auth_headers, fake_task_for_delete):

    response = client.delete(f"/tasks/delete?title={fake_task_for_delete.title}", 
                             headers=user_auth_headers)
    
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.delete
def test_delete_task_not_exists(client, admin_auth_headers):

    response = client.delete(f"/tasks/delete?title=anytitle", 
                             headers=admin_auth_headers)
    
    assert response.status_code == 404
    assert "Task not found" in response.text
    
@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.delete
def test_delete_done_tasks(client, admin_auth_headers, fake_tasks_for_delete):

    response = client.delete(f"/tasks/delete-done-task", 
                             headers=admin_auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "deleted"
    assert len(data["tasks"]) >= 20

@pytest.mark.tasks_api
@pytest.mark.admin
@pytest.mark.delete
def test_delete_expired_tasks(client, admin_auth_headers, fake_tasks_for_delete):

    response = client.delete(f"/tasks/delete-expired-task", 
                             headers=admin_auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "deleted"
    assert len(data["tasks"]) >= 20
