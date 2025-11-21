import pytest
from tests.fixtures.fake_users import fake_users

@pytest.mark.users_api
@pytest.mark.admin
@pytest.mark.get
def test_get_my_info(client, admin_auth_headers, fake_users):
    response = client.get("/users/me", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testadmin"

@pytest.mark.users_api
@pytest.mark.admin
@pytest.mark.get
def test_get_all_users_admin(client, admin_auth_headers, fake_users):
    response = client.get("/users/get-all-users?skip=0&limit=10", headers=admin_auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["users"], list)
    if data["users"]:
        assert "id" in data["users"][0]
        assert "username" in data["users"][0]
        assert len(data["users"]) == 10

@pytest.mark.users_api
@pytest.mark.non_admin
@pytest.mark.get
def test_get_all_users_non_admin(client, user_auth_headers):
    response = client.get("/users/get-all-users?skip=0&limit=10", headers=user_auth_headers)
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.users_api
@pytest.mark.admin
@pytest.mark.get
def test_get_all_users_by_search(client, admin_auth_headers):
    response = client.get("/users/get-all-users?search=user", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["users"], list)
    if data["users"]:
        assert "id" in data["users"][0]
        assert "username" in data["users"][0]

@pytest.mark.users_api
@pytest.mark.admin
@pytest.mark.get
def test_get_all_users_by_role(client, admin_auth_headers):
    response = client.get("/users/get-all-users?role=manager", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["users"], list)
    if data["users"]:
        assert "id" in data["users"][0]
        assert "username" in data["users"][0]

@pytest.mark.users_api
@pytest.mark.admin
@pytest.mark.get
def test_get_all_users_by_role(client, admin_auth_headers):
    response = client.get("/users/get-all-users?role=manager", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["users"], list)
    if data["users"]:
        assert "id" in data["users"][0]
        assert "username" in data["users"][0]

@pytest.mark.users_api
@pytest.mark.admin
@pytest.mark.get
def test_get_user_by_id(client, admin_auth_headers, test_admin):
    test_id = test_admin.id
    response = client.get(f"/users/get-user-by-id/{test_id}", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["users"]["username"] == test_admin.username

@pytest.mark.users_api
@pytest.mark.admin
@pytest.mark.get
def test_get_user_by_username(client, admin_auth_headers, test_admin):
    test_name = test_admin.username
    response = client.get(f"/users/get-user-by-username/{test_name}", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["users"]["id"] == test_admin.id
