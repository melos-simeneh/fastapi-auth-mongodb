from pydantic import BaseModel, EmailStr, Field

class SignupReqBody(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str

