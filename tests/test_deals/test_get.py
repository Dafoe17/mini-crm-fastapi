import pytest
from tests.fixtures.fake_deals import fake_deals
from tests.fixtures.fake_clients import fake_client_with_no_user

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.get
def test_get_all_deals_admin(client, admin_auth_headers, fake_deals):
    response = client.get("/deals/get-all?skip=0&limit=10", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["deals"], list)
    if data["deals"]:
        assert "id" in data["deals"][0]
        assert "title" in data["deals"][0]
        assert len(data["deals"]) == 10
    
@pytest.mark.deals_api
@pytest.mark.non_admin
@pytest.mark.get
def test_get_all_clients_non_admin(client, user_auth_headers):
    response = client.get("/deals/get-all?skip=0&limit=10", headers=user_auth_headers)
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.get
def test_get_deals_by_date(client, admin_auth_headers, fake_deals):
    response = client.get("/deals/get-by-date?skip=0&limit=10&date_field=created_at&new=true", 
                          headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["deals"], list)
    if data["deals"]:
        assert "id" in data["deals"][0]
        assert "title" in data["deals"][0]
        assert len(data["deals"]) == 10

