import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status, Depends

from jose import JWTError
from sqlalchemy.orm import Session
from app import db
from app.api.dependencies.auth import get_current_user
from app.core import jwt
from app.core.google_auth import verify_google_token
from app.core.jwt import create_access_token, create_refresh_token
from app.core.security import hash_password, verify_password
from app.db.session import get_db

from app.models.cart import Cart
from app.models.user import AuthProvider, CustomerProfile, User, UserRole
from app.schemas.auth_schema import GoogleAuthRequest, LoginRequest, RegisterRequest, TokenResponse, UserResponse

    
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        User.email == payload.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        phone_number=payload.phone_number,
        role=UserRole.CUSTOMER,
        auth_provider=AuthProvider.LOCAL
    )
    db.add(user)
    db.flush()

    customer_profile = CustomerProfile(
        user_id=user.id,
    )
    db.add(customer_profile)
    db.flush()

    cart = Cart(
        customer_id=customer_profile.id,
    )
    db.add(cart)

    db.commit()
    db.refresh(user)

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })

    refresh_token = create_refresh_token({
        "sub": str(user.id),
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/google",
    response_model=TokenResponse
)
def google_auth(
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db),
):
    google_user = verify_google_token(
        payload.credential
    )

    email = google_user.get("email")
    name = google_user.get("name")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account email is not found"
        )
    
    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        user = User(
            full_name=name,
            email=email,
            hashed_password=None,
            role=UserRole.CUSTOMER,
            auth_provider=AuthProvider.GOOGLE
        )
        db.add(user)
        db.flush()

        customer_profile = CustomerProfile(
            user_id=user.id
        )

        db.add(customer_profile)
        db.flush()

        cart = Cart(
            customer_id=customer_profile.id
        )

        db.add(cart)

        db.commit()
        db.refresh(user)

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })

    refresh_token = create_refresh_token({
        "sub": str(user.id)
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == payload.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found"
        )
    if not verify_password(
        payload.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })

    refresh_token = create_refresh_token({
        "sub": str(user.id),
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role.value
    }


@router.post("/refresh")
def refresh_token(
    refresh_token: str
):

    try:

        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type"
            )

        user_id = payload.get("sub")

        user = db.query(User).filter(
              User.id == user_id
            ).first()
        
        if not user:
            raise HTTPException(status_code=401,details="User not found")

        if not user.is_active :
            raise HTTPException(status_code=403,details="Account is deactivated")
        
        access_token = create_access_token({
            "sub": user_id,
            "role": user.role.value
        })

        return {
            "access_token": access_token
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )


@router.post("/logout")
def logout():
    return {
        "message": "Logged out successfully"
    }

