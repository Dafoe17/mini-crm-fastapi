import pytest
from tests.fixtures.fake_clients import fake_client_for_delete

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.delete
def test_delete_client_admin(client, admin_auth_headers, fake_client_for_delete):
    
    response = client.delete(f"/clients/delete/{fake_client_for_delete.name}", 
                        headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "deleted"
    assert data["clients"]["name"] == fake_client_for_delete.name

@pytest.mark.clients_api
@pytest.mark.non_admin
@pytest.mark.delete
def test_delete_client_non_admin(client, user_auth_headers, fake_client_for_delete):

    response = client.delete(f"/clients/delete/{fake_client_for_delete.name}", 
                        headers=user_auth_headers)

    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.delete
def test_delete_client_not_exists(client, admin_auth_headers):

    response = client.delete(f"/clients/delete/anyname", 
                        headers=admin_auth_headers)

    assert response.status_code == 404
    assert 'Client not found' in response.text
