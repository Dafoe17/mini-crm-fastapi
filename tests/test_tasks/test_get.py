import pytest
from tests.fixtures.fake_tasks import fake_tasks

@pytest.mark.tasks_api
@pytest.mark.non_admin
@pytest.mark.admin
@pytest.mark.get
def test_get_all_tasks(client, admin_auth_headers, fake_tasks):
    response = client.get("/tasks/get?skip=0&limit=10", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["tasks"], list)
    if data["tasks"]:
        assert "id" in data["tasks"][0]
        assert "title" in data["tasks"][0]
        assert len(data["tasks"]) == 10
