import pytest

from tests.fixtures.fake_clients import fake_client_with_no_user

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.non_admin
@pytest.mark.patch
def test_take_unassigned_client(client, admin_auth_headers, fake_client_with_no_user):
    response = client.patch(f"/clients/patch/take?name={fake_client_with_no_user.name}", 
                            headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "changed"

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.patch
def test_delegete_admin(client, admin_auth_headers, fake_client_with_no_user, test_admin):
    response = client.patch(
        f"/clients/patch/delegate?name={fake_client_with_no_user.name}&username={test_admin.username}", 
        headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "changed" 

@pytest.mark.clients_api
@pytest.mark.admin
@pytest.mark.patch
def test_delegete_admin_user_not_exists(client, admin_auth_headers, fake_client_with_no_user):
    response = client.patch(
        f"/clients/patch/delegate?name={fake_client_with_no_user.name}&username=anyname", 
        headers=admin_auth_headers)
    assert response.status_code == 404
    assert "User not found" in response.text

@pytest.mark.clients_api
@pytest.mark.non_admin
@pytest.mark.patch
def test_delegete_non_admin(client, user_auth_headers, fake_client_with_no_user, test_user):
    response = client.patch(
        f"/clients/patch/delegate?name={fake_client_with_no_user.name}&username={test_user.username}", 
        headers=user_auth_headers)
    assert response.status_code == 403

@pytest.mark.clients_api
@pytest.mark.non_admin
@pytest.mark.patch
def test_discharge_admin(client, admin_auth_headers, fake_client_with_no_user):
    response = client.patch(
        f"/clients/patch/take?name={fake_client_with_no_user.name}", 
        headers=admin_auth_headers)
    assert response.status_code == 200

    response = client.patch(
        f"/clients/patch/discharge?name={fake_client_with_no_user.name}", 
        headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "changed" 

@pytest.mark.clients_api
@pytest.mark.non_admin
@pytest.mark.patch
def test_discharge_non_admin(client, user_auth_headers, fake_client_with_no_user):
    response = client.patch(
        f"/clients/patch/take?name={fake_client_with_no_user.name}", 
        headers=user_auth_headers)
    assert response.status_code == 200

    response = client.patch(
        f"/clients/patch/discharge?name={fake_client_with_no_user.name}", 
        headers=user_auth_headers)
    assert response.status_code == 403
    assert "Access denied" in response.text
