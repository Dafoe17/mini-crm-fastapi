import pytest
from tests.fixtures.fake_deals import fake_deal
from tests.fixtures.fake_clients import fake_client_with_no_user

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.patch
def test_set_close_date_admin(client, admin_auth_headers, fake_deal):
    response = client.patch(f"/deals/patch/set-close-date?date=2026-11-21&title={fake_deal.title}", 
                            headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "changed" 

@pytest.mark.deals_api
@pytest.mark.non_admin
@pytest.mark.patch
def test_set_close_date_non_admin(client, user_auth_headers, fake_deal):
    response = client.patch(f"/deals/patch/set-close-date?date=2026-11-21&title={fake_deal.title}", 
                            headers=user_auth_headers)
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.patch
def test_set_status_admin(client, admin_auth_headers, fake_deal):
    response = client.patch(f"/deals/patch/set-status?status=closed&title={fake_deal.title}", 
                            headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "changed" 
    assert data["deals"]["status"] == "closed" 

@pytest.mark.deals_api
@pytest.mark.non_admin
@pytest.mark.patch
def test_set_status_non_admin(client, user_auth_headers, fake_deal):
    response = client.patch(f"/deals/patch/set-status?status=closed&title={fake_deal.title}", 
                            headers=user_auth_headers)
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.patch
def test_set_status_invalid_status(client, admin_auth_headers, fake_deal):
    response = client.patch(f"/deals/patch/set-status?status=unknown&title={fake_deal.title}", 
                            headers=admin_auth_headers)
    assert response.status_code == 400
    assert "Input should be" in response.text
