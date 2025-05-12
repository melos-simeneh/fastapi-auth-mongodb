# FastAPI Advanced Auth with MongoDB

A robust FastAPI project that implements secure, scalable user authentication and role-based access control using MongoDB. It includes features like user signup, login, profile management, password change, and admin-only access. Rate limiting is enforced with SlowAPI to prevent abuse. The project includes an automated test suite with pytest, ensuring the reliability and correctness of authentication flows.

## 🚀 Features

- User Signup & Login with JWT
- Profile viewing and updating
- Password change with validation
- Role-based access (Admin-only routes)
- Rate limiting (5 requests/minute)
- MongoDB for user data storage

## 🛠️ Tech Stack

- **FastAPI** – Web framework
- **MongoDB** – NoSQL database
- **Pydantic** – Data validation
- **SlowAPI** – Rate limiting
- **JWT** – Authentication
- **Pytest** – Unit and integration testing

## 📂 Project Structure

fastapi-auth-mongodb/
├── main.py
├── `__tests__/`
│ └── integration/
│ └── unit/
│ └── conftest.py
├── routes/
│ └── auth_router.py
├── controllers/
│ └── auth_controller.py
├── schemas/
│ └── auth_schema.py
├── utils/
│ └── bcrypt_handler.py
│ └── db.py
│ └── exception_handlers.py
│ └── jwt_handler.py
│ └── rate_limiter.py
│ └── settings.py
├── .env
├── .gitignore
├── requirements.txt
├── pytest.ini
└── README.md

## 📦 Installation

1. **Clone the repository**  

   ```bash
    git clone https://github.com/melos-simeneh/fastapi-auth-mongo.git
    cd fastapi-auth-mongo
   ```

2. **Create a virtual environment**

   ```bash
    python -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set environment variables (or create a .env file)**

    ```env
    MONGO_URI=mongodb://localhost:27017
    MONGO_DB_NAME=auth_db
    MONGO_TEST_DB_NAME=auth_test_db
    SECRET_KEY = "your_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    ```

5. **Run the server**

    ```bash
    uvicorn main:app --reload --port 5000
    ```

## 🔐 Endpoints

| Method | Endpoint                         | Description                   | Auth Required | Role   |
|--------|----------------------------------|-------------------------------|---------------|--------|
| POST   | `/auth/signup`                   | User registration             | ❌            | Any    |
| POST   | `/auth/login`                    | User login                    | ❌            | Any    |
| GET    | `/auth/profile`                  | Get current user profile      | ✅            | Any    |
| PUT    | `/auth/users/{user_id}/profile`  | Update profile                | ✅            | Self   |
| POST   | `/auth/users/{user_id}/change-password` | Change password        | ✅            | Self   |
| GET    | `/auth/admin-only`               | Admin-only route              | ✅            | Admin  |
| GET    | `/auth/users`                    | List all users                | ✅            | Admin  |

## 📌 Notes

- All routes are rate-limited to **5 requests per minute** per IP using SlowAPI.

- JWT tokens are required in the `Authorization: Bearer <token>` header for protected routes.

## 🧪 Testing

This project uses [pytest](https://docs.pytest.org/) for unit and integration testing.

### Running Tests

To run all tests with default (minimal) output:

```bash
pytest
```

To run tests in **verbose** mode, showing each test function name and result:

```bash
pytest -v
```
