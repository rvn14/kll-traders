from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
import os

from sqlalchemy.orm import Session
from app.db.session import get_db
from fastapi import Depends, HTTPException
from app.models.user import User

from dotenv import load_dotenv



load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid_token"
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    if not user:
        raise credentials_exception
    
    return user 
