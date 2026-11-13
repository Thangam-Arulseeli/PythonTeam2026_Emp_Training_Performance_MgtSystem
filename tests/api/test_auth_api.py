from fastapi import HTTPException


# regsiter endpoint
# register sucess
def test_register_success(client,api_service):
    reponse = client.post(
        "/api/auth/register",
        json ={
            "username" :"ramesh",
            "email":"ramesh.trainer@gmail.com",
            "password":"ramesh1234",
            "role":"trainer"
        }
    )

    assert reponse.status_code == 201
    assert reponse.json()["message"] == "Registration successful. You can now log in."

# registering with admin role - invalid
def test_register_invalid_role(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username":"admin",
            "email":"admin@gmail.com",
            "password":"admin1234",
            "role":"admin"
        }
    )
    assert response.status_code == 422

# registering with invalid email
def test_register_invalid_email(client):
    response = client.post(
        "/api/auth/register",
        json ={
            "username":"ramesh",
            "email":"invalid-email",
            "password":"ramesh1234",
            "role":"trainer"
        }
    )

    assert response.status_code == 422

# regsiter with short password(min length is 8)
def test_register_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username" : "ramesh",
            "email" :"ramesh.trainer@gmail.com",
            "password":"123",
            "role":"trainer"
        }
    )
    assert response.status_code == 422

# register with email which doesnot exists in the trainer or employee table
def test_register_staff_email_not_fount(client,api_service):
    api_service.register.side_effect = HTTPException(
        status_code=403,
        detail="Email is not registered as an active trainer"
    )

    response = client.post(
        "/api/auth/register",
        json={
            "username": "unknown",
            "email": "unknown@gmail.com",
            "password": "unknown123",
            "role": "trainer"
        }
    )
    assert response.status_code ==403

# register with duplicate email
def test_register_duplicate_email(client,api_service):
    api_service.register.side_effect = HTTPException(
        status_code=409,
        detail="Email is aleady registered"
    )
    response = client.post(
        "/api/auth/register",
        json={
            "username": "ramesh",
            "email": "ramesh.trainer@gmail.com",
            "password": "ramesh1234",
            "role": "trainer"
        }
    )
    assert response.status_code ==409

# register with duplicate username
def test_register_duplicate_username(client, api_service):
    api_service.register.side_effect = HTTPException(
        status_code=409,
        detail="Username is already taken"
    )

    response = client.post(
        "/api/auth/register",
        json={
            "username": "ramesh",
            "email": "another@gmail.com",
            "password": "ramesh1234",
            "role": "trainer"
        }
    )

    assert response.status_code == 409



# login endpoint
# login success
def test_login_success(client,api_service):
    api_service.login.return_value ={
        "access_token":"test-access-token",
        "refresh_token":"test-refresh-token",
        "token_type":"bearer"
    }

    response = client.post(
        "/api/auth/login",
        data={
            "username":"ramesh",
            "password":"ramesh1234"
        }
    )
    assert response.status_code == 200
    assert response.json()["access_token"] == "test-access-token"
    assert response.json()["refresh_token"] == "test-refresh-token"
    assert response.json()["token_type"]=="bearer"


# login with invalid credentials
def test_login_invalid_credentials(client,api_service):
    api_service.login.side_effect = HTTPException(
        status_code=401,
        detail="Invalid username or password"
    )
    response = client.post(
        "/api/auth/login",
        data={
            "username":"wrong",
            "password":"wrongpassword"
        }
    )
    assert response.status_code == 401

# login with inactive user credentials
def test_login_inactive_user(client,api_service):
    api_service.login.side_effect = HTTPException(
        status_code=403,
        detail="User account is inactive"
    )
    response = client.post(
        "/api/auth/login",
        data ={
            "username":"inactive",
            "password":"password123"
        }
    )
    assert response.status_code == 403


# login without password
def test_login_missing_password(client):
    response = client.post(
        "/api/auth/login",
        data={"username":"ramesh"}
    )
    assert response.status_code == 422




# refresh token endpoint
# refresh success
def test_refresh_success(client,api_service):
    api_service.refresh_tokens.return_value = {
        "access_token" :"new-access-token",
        "refresh_token" :"new-refresh-token",
        "token_type":"bearer"
    }
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token":"a"*30}
    )
    assert response.status_code ==200
    assert response.json()["access_token"] == "new-access-token"
    assert response.json()["refresh_token"] == "new-refresh-token"

# refresh with missing token
def test_refresh_missing_token(client):
    response = client.post(
        "/api/auth/refresh",
        json={}
    )
    assert response.status_code == 422

# refresh with invalid token
def test_refresh_invalid_token(client,api_service):
    api_service.refresh_tokens.side_effect = HTTPException(
        status_code=401,
        detail="Invalid or expired refresh token"
    )
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token":"a"*30}
    )
    assert response.status_code == 401

# logout endpoit
# logout success
def test_logout_success(client,api_service):
    response = client.post(
        "/api/auth/logout",
        json={"refresh_token":"a"*30}
    )

    assert response.status_code ==200
    assert response.json()["message"] == "Logged out successfully."

# logout with invalid refresh_token
def test_logout_invalid_refresh_token(client,api_service):
    api_service.logout.side_effect = HTTPException(
        status_code=401,
        detail="Invalid refresh token."
    )
    response = client.post(
        "/api/auth/logout",
        json={"refresh_token":"a"*30}
    )
    assert response.status_code == 401

# logout without access token
def test_logout_without_access_token(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/auth/logout",
        json={"refresh_token":"a"*30}
    )

# get current user profile endpoint
# get profile success
def test_get_profile_success(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "ramesh"
    assert response.json()["email"] == "ramesh.trainer@gmail.com"
    assert response.json()["role"] =="trainer"
    assert response.json()["is_active"] is True

# get profile without access token
def test_get_profile_without_access_token(unauthenticated_client):
    response = unauthenticated_client.get("/api/auth/me")
    assert response.status_code == 401

