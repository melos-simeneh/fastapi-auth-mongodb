import pytest
from fastapi.testclient import TestClient
from main import create_app
from motor.motor_asyncio import AsyncIOMotorClient

from utils.settings import MONGO_TEST_DB_NAME,MONGO_URI
from utils import jwt_handler
from routes import auth_routes


@pytest.fixture
async def test_mongo_connection():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_TEST_DB_NAME]
    # Check if 'users' collection exists
    if 'users' not in await db.list_collection_names():
        # Optionally create it or handle the scenario
        print("Users collection doesn't exist")
        
    yield db
    client.close()

@pytest.fixture
async def get_user_id(test_user_data,test_mongo_connection):
    user = await test_mongo_connection.users_collection.find_one({"email": test_user_data["email"]})
    assert user, f"User with email {test_user_data['email']} not found in database"
    return str(user["_id"])

@pytest.fixture
def reset_limiter():
    auth_routes.limiter.reset()


@pytest.fixture(scope="module")
def test_client():
    app = create_app(db_name=MONGO_TEST_DB_NAME)
    with TestClient(app) as client:
        yield client



@pytest.fixture
def test_user_data():
    return {
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "testpassword",
        "role": "user"
    }
@pytest.fixture
def test_user_data2():
    return {
        "full_name": "Test User2",
        "email": "test2@example.com",
        "password": "testpassword",
        "role": "user"
    }

@pytest.fixture
def test_admin_data():
    return {
        "full_name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpassword",
        "role": "admin"
    }
@pytest.fixture
def user_id(test_client,test_user_data,reset_limiter):
    response = test_client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    data = response.json()
    assert  data["success"] is True, data
    assert "access_token" in data
    
    payload=jwt_handler.verify_token(data["access_token"])
    user_id=payload.get("sub")
    return user_id
@pytest.fixture
def auth_headers(test_client, test_user_data,reset_limiter):
    # Helper to get auth headers for a test user
    response = test_client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def create_admin(test_client, test_admin_data):
    signup_response = test_client.post("/auth/signup", json=test_admin_data)
    assert signup_response.status_code == 200, f"Failed to create admin test user: {signup_response.json()}"
    
@pytest.fixture
async def admin_headers(test_client, test_admin_data):
    # Then try to login
    response = test_client.post("/auth/login", json={
        "email": test_admin_data["email"],
        "password": test_admin_data["password"]
    })
    
    # Check if login was successful
    assert response.status_code == 200, "Admin login failed"
    data = response.json()
    assert "access_token" in data, "Login response missing access_token"
    
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}