import pytest
from fastapi import status
from routes import auth_routes



@pytest.mark.asyncio
async def test_signup_success(test_client, test_user_data):
    response = test_client.post("/auth/signup", json=test_user_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "User created successfully"
    assert data["user"]["email"] == test_user_data["email"]
    assert "password" not in data["user"]  # Password should not be returned

@pytest.mark.asyncio
async def test_signup_duplicate_email(test_client, test_user_data):
    # First signup should succeed
    test_client.post("/auth/signup", json=test_user_data)
    
    # Second attempt with same email should fail
    response = test_client.post("/auth/signup", json=test_user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["message"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_success(test_client, test_user_data):
    # First create a user
    test_client.post("/auth/signup", json=test_user_data)
    
    # Then try to login
    response = test_client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(test_client, test_user_data):
    # Create a user
    test_client.post("/auth/signup", json=test_user_data)
    
    # Try to login with wrong password
    response = test_client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": "wrongpassword"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["message"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_profile_unauthorized(test_client):
    response = test_client.get("/auth/profile")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_profile_success(test_client, auth_headers):
    response = test_client.get("/auth/profile", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert "user" in data
    assert "email" in data["user"]

@pytest.mark.asyncio
async def test_admin_only_non_admin(test_client,create_admin, auth_headers):
    response = test_client.get("/auth/admin-only", headers=auth_headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["message"] == "Access denied. Admins only"

@pytest.mark.asyncio
async def test_admin_only_success(test_client, admin_headers,reset_limiter):

    response = test_client.get("/auth/admin-only", headers=admin_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["user"]["role"] == "admin"

@pytest.mark.asyncio
async def test_update_profile_success(test_client, auth_headers,user_id):

    # Update the profile
    update_data = {"full_name": "Updated Name"}
    response = test_client.put(
        f"/auth/users/{user_id}/profile",
        json=update_data,
        headers=auth_headers
    )
    
    data = response.json()
    assert response.status_code == status.HTTP_200_OK,data
    assert data["success"] is True
    assert data["user"]["full_name"] == "Updated Name"

@pytest.mark.asyncio
async def test_change_password_success(test_client, auth_headers,user_id, test_user_data):
    # First create a user and get their ID
    auth_routes.limiter.reset()
    
    print(user_id)
    # Change the password
    change_data = {
        "current_password": test_user_data["password"],
        "new_password":  test_user_data["password"]
    }
    response = test_client.post(
        f"/auth/users/{user_id}/change-password",
        json=change_data,
        headers=auth_headers
    )
    
    data = response.json()
    assert response.status_code == status.HTTP_200_OK,data
    print(user_id,auth_headers)
    assert data["success"] is True
    
    # Verify the new password works
    login_response = test_client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    assert login_response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_list_users_non_admin(test_client, auth_headers):
    response = test_client.get("/auth/users", headers=auth_headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_list_users_success(test_client, admin_headers, test_user_data, test_admin_data):
    # Create some test users
    test_client.post("/auth/signup", json=test_user_data)
    test_client.post("/auth/signup", json=test_admin_data)
    
    # List users as admin
    response = test_client.get("/auth/users", headers=admin_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["count"] >= 2  # At least the two we just created
    assert any(user["role"] == "admin" for user in data["users"])
    assert any(user["role"] == "user" for user in data["users"])

@pytest.mark.asyncio
async def test_rate_limiting(test_client, test_user_data2,reset_limiter):
    # Test the rate limiting on signup endpoint
    responses = []
    for _ in range(6):  # One more than the limit
        response = test_client.post("/auth/signup", json=test_user_data2)
        responses.append(response.status_code)
    
    # First 5 should be successful (400 for duplicate after first), 6th should be 429
    assert responses.count(200) == 1,responses  # First request succeeds
    assert responses.count(400) >= 4,responses  # Next 5 fail due to duplicate email
    assert 429 in responses,responses  # The 6th request should be rate limited
    
