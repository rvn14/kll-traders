from typing import Annotated

from sqlalchemy.orm import Session

from app.db.session import get_db
from fastapi import Depends
from app.repositories.admin_user_repository import AdminUserRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.customer_profile_repository import CustomerProfileRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.settings_repository import SettingsRepository
from app.services.blob_service import AzureBlobService
from app.services.admin_user_service import AdminUserService
from app.services.cart_service import CartService
from app.services.customer_profile_service import CustomerProfileService
from app.services.item_service import ItemService
from app.services.order_service import OrderService
from app.services.settings_service import SettingsService
from app.services.whatsapp_service import WhatsAppService
from app.repositories.category_repository import CategoryRepository
from app.services.category_service import CategoryService
from app.repositories.brand_repository import BrandRepository
from app.services.brand_service import BrandService

def get_category_repository(
    db: Annotated[Session, Depends(get_db)],
) -> CategoryRepository:
    return CategoryRepository(db)

def get_category_service(
    category_repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> CategoryService:
    return CategoryService(category_repository)


def get_brand_repository(
    db: Annotated[Session, Depends(get_db)],
) -> BrandRepository:
    return BrandRepository(db)


def get_brand_service(
    brand_repository: Annotated[BrandRepository, Depends(get_brand_repository)],
) -> BrandService:
    return BrandService(brand_repository)


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


def get_customer_profile_repository(
    db: Annotated[Session, Depends(get_db)],
) -> CustomerProfileRepository:
    return CustomerProfileRepository(db)


def get_customer_profile_service(
    profile_repository: Annotated[CustomerProfileRepository, Depends(get_customer_profile_repository)]
) -> CustomerProfileService:
    return CustomerProfileService(profile_repository)


def get_cart_repository(
    db: Annotated[Session, Depends(get_db)],
) -> CartRepository:
    return CartRepository(db)


def get_cart_service(
    cart_repository: Annotated[CartRepository, Depends(get_cart_repository)],
    profile_repository: Annotated[
        CustomerProfileRepository, Depends(get_customer_profile_repository)
    ],
    item_repository: Annotated[ItemRepository, Depends(get_item_repository)],
) -> CartService:
    return CartService(
        cart_repository=cart_repository,
        customer_profile_repository=profile_repository,
        item_repository=item_repository,
    )


def get_settings_repository(
    db: Annotated[Session, Depends(get_db)],
) -> SettingsRepository:
    return SettingsRepository(db)


def get_settings_service(
    settings_repository: Annotated[SettingsRepository, Depends(get_settings_repository)],
) -> SettingsService:
    return SettingsService(settings_repository)


def get_order_repository(
    db: Annotated[Session, Depends(get_db)],
) -> OrderRepository:
    return OrderRepository(db)


def get_whatsapp_service() -> WhatsAppService:
    return WhatsAppService()


def get_order_service(
    order_repository: Annotated[OrderRepository, Depends(get_order_repository)],
    cart_repository: Annotated[CartRepository, Depends(get_cart_repository)],
    item_repository: Annotated[ItemRepository, Depends(get_item_repository)],
    customer_profile_repository: Annotated[CustomerProfileRepository, Depends(get_customer_profile_repository)],
    settings_repository: Annotated[SettingsRepository, Depends(get_settings_repository)],
    whatsapp_service: Annotated[WhatsAppService, Depends(get_whatsapp_service)],
) -> OrderService:
    return OrderService(
        order_repository=order_repository,
        cart_repository=cart_repository,
        item_repository=item_repository,
        customer_profile_repository=customer_profile_repository,
        settings_repository=settings_repository,
        whatsapp_service=whatsapp_service,
    )
