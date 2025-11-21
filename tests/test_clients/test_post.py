import pytest

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.post
def test_add_client_admin(client, admin_auth_headers, test_admin):
    new_client = {
        "name": "New_client",
        "email": "client123@email.com",
        "password": "89999999999",
        "notes": "",
        "user_name": test_admin.username 
    }

    response = client.post(f"/clients/add", 
                            headers=admin_auth_headers, json=new_client)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "created"
    assert data["clients"]["name"] == "New_client"

@pytest.mark.clients_api
@pytest.mark.non_admin
@pytest.mark.post
def test_add_client_non_admin(client, user_auth_headers, test_user):
    new_client = {
        "name": "New_client",
        "email": "client123@email.com",
        "password": "89999999999",
        "notes": "",
        "user_name": test_user.username
    }

    response = client.post(f"/clients/add", 
                            headers=user_auth_headers, json=new_client)
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.post
def test_add_client_invalid_email(client, admin_auth_headers, test_admin):
    new_client = {
        "name": "New_client",
        "email": "client123",
        "password": "89999999999",
        "notes": "",
        "user_name": test_admin.username 
    }

    response = client.post(f"/clients/add", 
                            headers=admin_auth_headers, json=new_client)
    assert response.status_code == 400
    assert 'value is not a valid email address' in response.text

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.post
def test_add_client_user_already_exists(client, admin_auth_headers, test_admin):
    new_client = {
        "name": "New_client_exists",
        "email": "client123@email.com",
        "password": "89999999999",
        "notes": "",
        "user_name": test_admin.username 
    }

    response = client.post(f"/clients/add", 
                            headers=admin_auth_headers, json=new_client)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "created"
    assert data["clients"]["name"] == "New_client_exists"

    response = client.post(f"/clients/add", 
                            headers=admin_auth_headers, json=new_client)
    assert response.status_code == 409
    assert 'Client already exists' in response.text
