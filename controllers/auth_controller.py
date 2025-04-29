from fastapi import HTTPException
from utils.db import mongo_connection
from schemas.auth_schema import SignupReqBody
from utils import jwt

async def create_user(user: SignupReqBody):
    existing_user = await mongo_connection.users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = await jwt.hash_password(user.password)

    user_dict = {
        "full_name": user.full_name,
        "email": user.email,
        "password": hashed_pw,
        "role": user.role
    }

    result = await mongo_connection.users_collection.insert_one(user_dict)

    return {
        "user": {
            "_id": str(result.inserted_id),
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }
