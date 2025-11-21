def test_add_user_admin(client, admin_auth_headers):
    new_user = {
        "username": "newuser",
        "role": "user",
        "password": "Abc123!@#"
    }

    response = client.post("/users/add", headers=admin_auth_headers, json=new_user)
    assert response.status_code == 200

    data = response.json()
    assert "status" in data  
    assert data["status"] == "created"
    assert data["users"]["username"] == "newuser"

def test_add_user_non_admin(client, user_auth_headers):
    new_user = {
        "username": "newuser",
        "role": "user",
        "password": "Abc123!@#"
    }

    response = client.post("/users/add", headers=user_auth_headers, json=new_user)
    assert response.status_code == 403

def test_add_user_invalid_password(client, admin_auth_headers):
    new_user = {
        "username": "newuser",
        "role": "user",
        "password": "Abc123"
    }

    response = client.post("/users/add", headers=admin_auth_headers, json=new_user)
    assert response.status_code == 400
    assert "Invalid password. " in response.text

def test_add_user_already_exists(client, admin_auth_headers):
    new_user = {
        "username": "testadmin",
        "role": "user",
        "password": "Abc123!@#"
    }

    response = client.post("/users/add", headers=admin_auth_headers, json=new_user)
    assert response.status_code == 400
    assert "already exists" in response.text

def test_add_user_role_out_of_enum(client, admin_auth_headers):
    new_user = {
        "username": "testadmin",
        "role": "god",
        "password": "Abc123!@#"
    }

    response = client.post("/users/add", headers=admin_auth_headers, json=new_user)
    assert response.status_code == 400
    assert "Input should be" in response.text

def test_add_user_with_short_name(client, admin_auth_headers):
    new_user = {
        "username": "r",
        "role": "user",
        "password": "Abc123!@#"
    }

    response = client.post("/users/add", headers=admin_auth_headers, json=new_user)
    assert response.status_code == 400
    assert "String should have at least 2 characters" in response.text
