from typing import Optional
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    phone_number: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class GoogleAuthRequest(BaseModel):
    credential: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str