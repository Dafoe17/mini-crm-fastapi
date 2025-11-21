def test_put_user_admin(client, admin_auth_headers, test_admin):
    update_user = {
        "username": "testadmin_updated",
        "role": "admin",
        "password": "Abc123!@#"
    }

    username = test_admin.username 
    response = client.put(f"/users/update/{username}", headers=admin_auth_headers, json=update_user)
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "changed"
    assert data["users"]["username"] == "testadmin_updated"

def test_put_user_non_admin(client, user_auth_headers, test_user):
    update_user = {
        "username": "testuser_updated",
        "role": "admin",
        "password": "Abc123!@#"
    }

    username = test_user.username 
    response = client.put(f"/users/update/{username}", headers=user_auth_headers, json=update_user)
    assert response.status_code == 403

def test_put_user_not_exists(client, admin_auth_headers):
    update_user = {
        "username": "testadmin_updated",
        "role": "admin",
        "password": "Abc123!@#"
    }

    username = "any_name"
    response = client.put(f"/users/update/{username}", headers=admin_auth_headers, json=update_user)
    assert response.status_code == 404
    assert "User not found" in response.text

def test_put_user_invalid_password(client, admin_auth_headers, test_admin):
    update_user = {
        "username": "testadmin_updated",
        "role": "admin",
        "password": "Abc123"
    }

    username = test_admin.username
    response = client.put(f"/users/update/{username}", headers=admin_auth_headers, json=update_user)
    assert response.status_code == 400
    assert "Invalid password. " in response.text

def test_add_user_role_out_of_enum(client, admin_auth_headers, test_admin):
    update_user = {
        "username": "testadmin_updated",
        "role": "god",
        "password": "Abc123!@#"
    }

    username = test_admin.username
    response = client.put(f"/users/update/{username}", headers=admin_auth_headers, json=update_user)
    assert response.status_code == 400
    assert "Input should be" in response.text

def test_add_user_role_out_of_enum(client, admin_auth_headers, test_admin):
    update_user = {
        "username": "t",
        "role": "admin",
        "password": "Abc123!@#"
    }

    username = test_admin.username
    response = client.put(f"/users/update/{username}", headers=admin_auth_headers, json=update_user)
    assert response.status_code == 400
    assert "String should have at least 2 characters" in response.text
