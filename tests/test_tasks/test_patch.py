import pytest
from tests.fixtures.fake_tasks import fake_task

@pytest.mark.tasks_api
@pytest.mark.non_admin
@pytest.mark.admin
@pytest.mark.get
def test_take_task(client, admin_auth_headers, fake_task):
    response = client.patch(f"/tasks/take?title={fake_task.title}", 
                            headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "changed"

@pytest.mark.tasks_api
@pytest.mark.non_admin
@pytest.mark.admin
@pytest.mark.get
def test_take_task_not_exist(client, admin_auth_headers):
    response = client.patch(f"/tasks/take?title=anytitle", 
                            headers=admin_auth_headers)
    assert response.status_code == 404
    assert "Task not found" in response.text
