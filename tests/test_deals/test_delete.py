import pytest
from tests.fixtures.fake_deals import fake_deals_for_delete, fake_deal_for_delete
from tests.fixtures.fake_clients import fake_client_with_no_user

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.delete
def test_delete_deal_admin(client, admin_auth_headers, fake_deal_for_delete):

    response = client.delete(f"/deals/delete?title={fake_deal_for_delete.title}", 
                            headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "deleted"
    assert data["deals"]["title"] == fake_deal_for_delete.title

@pytest.mark.deals_api
@pytest.mark.non_admin
@pytest.mark.delete
def test_delete_deal_non_admin(client, user_auth_headers, fake_deal_for_delete):

    response = client.delete(f"/deals/delete?title={fake_deal_for_delete.title}", 
                            headers=user_auth_headers)
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.delete
def test_delete_deal_not_exists(client, admin_auth_headers):

    response = client.delete(f"/deals/delete?title=anytitle", 
                            headers=admin_auth_headers)
    assert response.status_code == 404
    assert "Deal not found" in response.text

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.delete
def test_delete_by_client_admin(client, admin_auth_headers, fake_deals_for_delete):
    response = client.delete(f"/deals/delete-by-client?client_id={fake_deals_for_delete[0].client_id}", 
                            headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "deleted"
    assert len(data["deals"]) == 20

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.delete
def test_delete_by_client_non_admin(client, user_auth_headers, fake_deals_for_delete):
    response = client.delete(f"/deals/delete-by-client?client_id={fake_deals_for_delete[0].client_id}", 
                            headers=user_auth_headers)
    assert response.status_code == 403
    assert "Access denied" in response.text

@pytest.mark.deals_api
@pytest.mark.admin
@pytest.mark.delete
def test_delete_by_client_not_exists(client, admin_auth_headers, fake_deals_for_delete):
    response = client.delete(f"/deals/delete-by-client?client_name=anyname", 
                            headers=admin_auth_headers)
    assert response.status_code == 404
    assert "No deals for this client" in response.text
