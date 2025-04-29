from fastapi import HTTPException,status,Depends
from utils.db import mongo_connection
from schemas.auth_schema import SignupReqBody,LoginReqBody
from utils import bcrypt_handler,jwt_handler
from fastapi.security import HTTPBearer
from bson import ObjectId
auth_scheme = HTTPBearer(scheme_name="Bearer", auto_error=False)

async def create_user(user: SignupReqBody):
    existing_user = await mongo_connection.users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = bcrypt_handler.hash_password(user.password)

    user_dict = {
        "full_name": user.full_name,
        "email": user.email,
        "password": hashed_pw,
        "role": user.role
    }

    result = await mongo_connection.users_collection.insert_one(user_dict)

    return {
        "success":True,
        "message":"User created successfully",
        "user": {
            "_id": str(result.inserted_id),
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }


async def login_handler(data:LoginReqBody):
    user = await mongo_connection.users_collection.find_one({"email": data.email})
    print(user)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not bcrypt_handler.verify_password(data.password, user['password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = jwt_handler.create_token(user_id=str(user["_id"]))
    
    return {
            "success":True,
            "message":"User logged in successfully",
            "access_token": token,
            "token_type": "bearer"
            }
    
async def get_current_user(token=Depends(auth_scheme)):    
    if token is None or token.credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing",
        )
    
    payload=jwt_handler.verify_token(token.credentials)
    user_id=payload.get("sub")
    
    if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )
        
    user =  await mongo_connection.users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return {
            "success":True,
            "message":"User profile fetched successfully",
            "user":{
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
    }