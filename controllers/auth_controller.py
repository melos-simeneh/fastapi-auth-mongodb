from fastapi import HTTPException,status,Depends,Request
from utils.db import mongo_connection
from schemas.auth_schema import SignupReqBody,LoginReqBody,ChangePasswordReq,UpdateProfileReq
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
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"]
            }


async def update_user_profile(
    user_id: str,
    update_data: UpdateProfileReq,
    current_user: dict
):
    if user_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own profile"
        )

    update_values = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    result = await mongo_connection.users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_values}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or no changes made"
        )

    updated_user = await mongo_connection.users_collection.find_one(
        {"_id": ObjectId(user_id)}
    )
    return {
        "success": True,
        "message": "Profile updated successfully",
        "user": {
            "id": str(updated_user["_id"]),
            "full_name": updated_user["full_name"],
            "email": updated_user["email"],
            "role": updated_user["role"]
        }
    }

async def change_user_password(
    user_id: str,
    passwords: ChangePasswordReq,
    current_user: dict
):
    if user_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only change your own password"
        )

    user = await mongo_connection.users_collection.find_one(
        {"_id": ObjectId(user_id)}
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not bcrypt_handler.verify_password(
        passwords.current_password, 
        user["password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    new_hashed_pw = bcrypt_handler.hash_password(passwords.new_password)
    
    await mongo_connection.users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": new_hashed_pw}}
    )

    return {
        "success": True,
        "message": "Password changed successfully"
    }

async def list_all_users(current_user: dict):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    users = []
    async for user in mongo_connection.users_collection.find():
        users.append({
            "id": str(user["_id"]),
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"]
        })

    return {
        "success": True,
        "count": len(users),
        "users": users
    }