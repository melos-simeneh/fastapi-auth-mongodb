from fastapi import APIRouter,Depends
from schemas.auth_schema import SignupReqBody,LoginReqBody
from controllers.auth_controller import create_user,login_handler,get_current_user

router = APIRouter(prefix="/auth",tags=["Authentication"])


@router.post("/signup")
async def signup(user: SignupReqBody):
    return await create_user(user)

@router.post("/login")
async def login(user: LoginReqBody):
    return await login_handler(user)

@router.get("/profile")
async def profile(current_user = Depends(get_current_user)):
    return current_user