def test_delete_user_admin(client, admin_auth_headers):
    new_user_for_delete = {
        "username": "newuser",
        "role": "user",
        "password": "Abc123!@#"
    }

    response = client.post("/users/add", headers=admin_auth_headers, json=new_user_for_delete)
    assert response.status_code == 200

    username = new_user_for_delete["username"]

    response = client.delete(f"/users/delete/{username}", headers=admin_auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert "status" in data  
    assert data["status"] == "deleted"
    assert data["users"]["username"] == "newuser"

def test_delete_user_non_admin(client, admin_auth_headers, user_auth_headers):
    new_user_for_delete = {
        "username": "newuser",
        "role": "user",
        "password": "Abc123!@#"
    }

    response = client.post("/users/add", headers=admin_auth_headers, json=new_user_for_delete)
    assert response.status_code == 200

    username = new_user_for_delete["username"]

    response = client.delete(f"/users/delete/{username}", headers=user_auth_headers)
    assert response.status_code == 403

    response = client.delete(f"/users/delete/{username}", headers=admin_auth_headers)
    assert response.status_code == 200

def test_delete_user_not_exists(client, admin_auth_headers):

    username = "any_name"

    response = client.delete(f"/users/delete/{username}", headers=admin_auth_headers)
    assert response.status_code == 404
