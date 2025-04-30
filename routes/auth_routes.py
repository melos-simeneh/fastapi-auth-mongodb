from fastapi import APIRouter,Depends,Request,HTTPException,Path
from schemas.auth_schema import SignupReqBody,LoginReqBody,UpdateProfileReq,ChangePasswordReq
from controllers.auth_controller import create_user,login_handler,get_current_user,update_user_profile,change_user_password,list_all_users
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/auth",tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/signup")
@limiter.limit("5/minute")
async def signup(request:Request,user: SignupReqBody):
    return await create_user(user)

@router.post("/login")
@limiter.limit("5/minute")
async def login(request:Request,user: LoginReqBody):
    return await login_handler(user)

@router.get("/profile") 
@limiter.limit("5/minute")
async def profile(request: Request,current_user = Depends(get_current_user)):
    return {
        "success": True,
        "message": "User profile fetched successfully",
        "user": current_user
    }


@router.get("/admin-only")
@limiter.limit("5/minute")
async def admin_only(request: Request, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only")
    return {
        "success": True,
        "message": "Access granted: Admins only",
        "user": current_user
    }


@router.put("/users/{user_id}/profile")
@limiter.limit("5/minute")
async def update_profile(
    request: Request,   
    user_id: str,
    update_data: UpdateProfileReq,
    current_user: dict = Depends(get_current_user)
):
    return await update_user_profile(user_id, update_data, current_user)

@router.post("/users/{user_id}/change-password")
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    user_id: str,
    data: ChangePasswordReq,
    current_user: dict = Depends(get_current_user)
):
    return await change_user_password(user_id, data, current_user)

@router.get("/users")
@limiter.limit("5/minute")
async def list_users(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only")
    return await list_all_users(current_user)