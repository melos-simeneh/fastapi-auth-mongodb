import pytest
from fastapi import HTTPException, status
from bson import ObjectId
from controllers.auth_controller import (
    create_user,
    login_handler,
    get_current_user,
    update_user_profile,
    change_user_password,
    list_all_users
)
from schemas.auth_schema import (
    SignupReqBody,
    LoginReqBody,
    UpdateProfileReq,
    ChangePasswordReq
)
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_create_user_success(mocker):
    # Mock the database find_one to return None (no existing user)
    mocker.patch(
        "controllers.auth_controller.mongo_connection.users_collection.find_one",
        new_callable=AsyncMock,
        return_value=None
    )
    
    # Mock the insert_one to return a mock inserted_id
    mock_insert = mocker.patch(
        "controllers.auth_controller.mongo_connection.users_collection.insert_one",
        new_callable=AsyncMock
    )
    mock_insert.return_value.inserted_id = ObjectId("507f1f77bcf86cd799439011")
    
    user_data = SignupReqBody(
        full_name="Test User",
        email="test@example.com",
        password="password123",
        role="user"
    )
    
    result = await create_user(user_data)
    
    assert result["success"] is True
    assert result["message"] == "User created successfully"
    assert result["user"]["email"] == "test@example.com"
    assert isinstance(result["user"]["_id"], str)

@pytest.mark.asyncio
async def test_create_user_duplicate_email(mocker):
    # Mock the database to return an existing user
    mocker.patch(
        "controllers.auth_controller.mongo_connection.users_collection.find_one",
        new_callable=AsyncMock,
        return_value={"email": "test@example.com"}
    )
    
    user_data = SignupReqBody(
        full_name="Test User",
        email="test@example.com",
        password="password123",
        role="user"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await create_user(user_data)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered"

@pytest.mark.asyncio
async def test_login_handler_success(mocker):
    # Mock bcrypt verify_password to return True
    mocker.patch(
        "controllers.auth_controller.bcrypt_handler.verify_password",
        return_value=True
    )
    
    # Mock the database to return a user
    mocker.patch(
        "controllers.auth_controller.mongo_connection.users_collection.find_one",
        new_callable=AsyncMock,
        return_value={
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "email": "test@example.com",
            "password": "hashedpassword",
            "role": "user"
        }
    )
    
    # Mock jwt create_token to return a dummy token
    mocker.patch(
        "controllers.auth_controller.jwt_handler.create_token",
        return_value="dummy_token"
    )
    
    login_data = LoginReqBody(
        email="test@example.com",
        password="password123"
    )
    
    result = await login_handler(login_data)
    
    assert result["success"] is True
    assert result["access_token"] == "dummy_token"

@pytest.mark.asyncio
async def test_login_handler_invalid_credentials(mocker):
    # Mock the database to return None (user not found)
    mocker.patch(
        "controllers.auth_controller.mongo_connection.users_collection.find_one",
        new_callable=AsyncMock,
        return_value=None
    )
    
    login_data = LoginReqBody(
        email="nonexistent@example.com",
        password="password123"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await login_handler(login_data)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid credentials"

@pytest.mark.asyncio
async def test_get_current_user_success(mocker):
    # Mock jwt verify_token to return a payload
    mocker.patch(
        "controllers.auth_controller.jwt_handler.verify_token",
        return_value={"sub": "507f1f77bcf86cd799439011"}
    )
    
    # Mock the database to return a user
    mocker.patch(
        "controllers.auth_controller.mongo_connection.users_collection.find_one",
        new_callable=AsyncMock,
        return_value={
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "user"
        }
    )
    
    # Mock the HTTPBearer dependency
    mock_token = type('MockToken', (), {'credentials': 'dummy_token'})
    
    result = await get_current_user(mock_token)
    
    assert result["email"] == "test@example.com"
    assert result["full_name"] == "Test User"

@pytest.mark.asyncio
async def test_get_current_user_missing_token():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(None)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Authorization token missing"

