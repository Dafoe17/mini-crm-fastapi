import pytest
from tests.fixtures.fake_clients import fake_clients

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.get
def test_get_all_clients_admin(client, admin_auth_headers, fake_clients):
    response = client.get("/clients/get?skip=0&limit=10", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["clients"], list)
    if data["clients"]:
        assert "id" in data["clients"][0]
        assert "name" in data["clients"][0]
        assert len(data["clients"]) == 10
    
@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.get
def test_get_all_clients_non_admin(client, user_auth_headers):
    response = client.get("/clients/get?skip=0&limit=10", headers=user_auth_headers)
    assert response.status_code == 403
    assert "Access denied" in response.text
