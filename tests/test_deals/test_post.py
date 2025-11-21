import pytest
from tests.fixtures.fake_deals import fake_deal
from tests.fixtures.fake_clients import fake_client_with_no_user

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.post
def test_post_deal_admin(client, admin_auth_headers, fake_client_with_no_user):
    new_deal = {
        "title": "New_deal",
        "status": "new",
        "value": 10000,
        "closed_at": None,
        "client_name": fake_client_with_no_user.name
    }

    response = client.post(f"/deals/add", 
                            headers=admin_auth_headers, json=new_deal)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "created"
    assert data["deals"]["title"] == "New_deal"

@pytest.mark.deals_api
@pytest.mark.non_admin
@pytest.mark.post
def test_post_deal_non_admin(client, user_auth_headers, fake_client_with_no_user):
    new_deal = {
        "title": "New_deal",
        "status": "new",
        "value": 10000,
        "closed_at": None,
        "client_name": fake_client_with_no_user.name
    }

    response = client.post(f"/deals/add", 
                            headers=user_auth_headers, json=new_deal)
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.post
def test_post_deal_invalid_title(client, admin_auth_headers, fake_client_with_no_user):
    new_deal = {
        "title": "N",
        "status": "new",
        "value": 10000,
        "closed_at": None,
        "client_name": fake_client_with_no_user.name
    }

    response = client.post(f"/deals/add", 
                            headers=admin_auth_headers, json=new_deal)
    assert response.status_code == 400
    assert "String should have at least 2 characters" in response.text

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.post
def test_post_deal_invalid_value(client, admin_auth_headers, fake_client_with_no_user):
    new_deal = {
        "title": "New_deal",
        "status": "new",
        "value": -1,
        "closed_at": None,
        "client_name": fake_client_with_no_user.name
    }

    response = client.post(f"/deals/add", 
                            headers=admin_auth_headers, json=new_deal)
    assert response.status_code == 400
    assert "Input should be greater than 0" in response.text

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.post
def test_post_deal_invalid_client_name(client, admin_auth_headers):
    new_deal = {
        "title": "New_deal",
        "status": "new",
        "value": 10000,
        "closed_at": None,
        "client_name": "anyname"
    }

    response = client.post(f"/deals/add", 
                            headers=admin_auth_headers, json=new_deal)
    assert response.status_code == 404
    assert "Client not found" in response.text
