import pytest
from tests.fixtures.fake_clients import fake_client_with_no_user

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.put
def test_update_client_admin(client, admin_auth_headers, test_admin, fake_client_with_no_user):
    updated_client = {
        "name": "Updated_client",
        "email": "client123@email.com",
        "password": "89999999999",
        "notes": "",
        "user_name": test_admin.username 
    }

    response = client.put(f"/clients/update?name={fake_client_with_no_user.name}", 
                            headers=admin_auth_headers, json=updated_client)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "changed"
    assert data["clients"]["name"] == "Updated_client"

@pytest.mark.clients_api
@pytest.mark.non_admin
@pytest.mark.put
def test_update_client_non_admin(client, user_auth_headers, test_user, fake_client_with_no_user):
    updated_client = {
        "name": "Updated_client",
        "email": "client123@email.com",
        "password": "89999999999",
        "notes": "",
        "user_name": test_user.username
    }

    response = client.put(f"/clients/update?name={fake_client_with_no_user.name}", 
                            headers=user_auth_headers, json=updated_client)
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.put
def test_update_client_invalid_email(client, admin_auth_headers, test_admin, fake_client_with_no_user):
    updated_client = {
        "name": "Updated_client",
        "email": "client123",
        "password": "89999999999",
        "notes": "",
        "user_name": test_admin.username 
    }

    response = client.put(f"/clients/update?name={fake_client_with_no_user.name}", 
                            headers=admin_auth_headers, json=updated_client)
    assert response.status_code == 400
    assert 'value is not a valid email address' in response.text

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.put
def test_update_client_not_exists(client, admin_auth_headers, test_admin):
    updated_client = {
        "name": "Updated_client",
        "email": "client123@email.com",
        "password": "89999999999",
        "notes": "",
        "user_name": test_admin.username 
    }

    response = client.put("/clients/update?name=anyname", 
                        headers=admin_auth_headers, json=updated_client)

    assert response.status_code == 404
    assert 'Client not found' in response.text
