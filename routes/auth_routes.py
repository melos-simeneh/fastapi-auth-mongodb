from fastapi import APIRouter
from schemas.auth_schema import SignupReqBody
from controllers.auth_controller import create_user

router = APIRouter(prefix="/auth",tags=["Authentication"])


@router.post("/signup")
async def signup(user: SignupReqBody):
    return await create_user(user)