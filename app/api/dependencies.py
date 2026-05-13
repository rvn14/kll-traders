from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.customer_repository import CustomerRepository
from app.repositories.item_repository import ItemRepository
from app.services.blob_service import AzureBlobService
from app.services.customer_service import CustomerService
from app.services.item_service import ItemService


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

