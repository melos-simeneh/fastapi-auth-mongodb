from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class SignupReqBody(BaseModel):
    full_name: str = Field(
        min_length=1,
        max_length=50,
        examples=["Melos Simeneh"],
        description="Non-empty full name with max 50 chars"
    )
    
    email: EmailStr = Field(
        examples=["user@example.com"],
        description="Valid email address"
    )
    
    password: str = Field(
        min_length=6,
        max_length=100,
        pattern=r"^\S+$",  # No whitespace allowed
        examples=["SecurePass123"],
        description="Password (6-100 chars, no spaces)"
    )
    
    role: UserRole = Field(
        default=UserRole.USER,
        examples=["user"],
        description="User role"
    )

    @field_validator('full_name')
    @classmethod
    def strip_and_validate_name(cls, v: str) -> str:
        if not (v := v.strip()):
            raise ValueError("Full name cannot be empty")
        return v