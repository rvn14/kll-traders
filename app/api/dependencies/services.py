from typing import Annotated

from sqlalchemy.orm import Session

from app.db.session import get_db
from fastapi import Depends
from app.repositories.admin_user_repository import AdminUserRepository
from app.repositories.item_repository import ItemRepository
from app.services.blob_service import AzureBlobService
from app.services.admin_user_service import AdminUserService
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


def get_admin_user_repository(
    db: Annotated[Session, Depends(get_db)],
) -> AdminUserRepository:
    return AdminUserRepository(db)

def get_admin_user_service(
    admin_user_repository: Annotated[AdminUserRepository, Depends(get_admin_user_repository)],
) -> AdminUserService:
    return AdminUserService(admin_user_repository)


