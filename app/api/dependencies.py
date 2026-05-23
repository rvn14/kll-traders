from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
import os
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.repositories.customer_repository import CustomerRepository
from app.repositories.item_repository import ItemRepository
from app.services.blob_service import AzureBlobService
from app.services.customer_service import CustomerService
from app.services.item_service import ItemService
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


def get_item_repository(
    db: Annotated[Session, Depends(get_db)],
) -> ItemRepository:
    return ItemRepository(db)


def get_item_service(
    item_repository: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemService:
    return ItemService(item_repository)


def get_blob_service() -> AzureBlobService:
    return AzureBlobService()


def get_customer_repository(
    db: Annotated[Session, Depends(get_db)],
) -> CustomerRepository:
    return CustomerRepository(db)

def get_customer_service(
    customer_repository: Annotated[CustomerRepository, Depends(get_customer_repository)],
) -> CustomerService:
    return CustomerService(customer_repository)


