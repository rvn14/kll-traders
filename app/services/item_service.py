from sqlalchemy.exc import IntegrityError
from app.core.exceptions import ItemAlreadyExistsError, ItemNotFoundError
from app.models.item import Item
from app.repositories.item_repository import ItemRepository
from app.models.user import User, UserRole
from fastapi import HTTPException

import math

from sqlalchemy.orm import Session

from app.repositories.item_repository import ItemRepository

from app.schemas.item_schema import (
    ItemQueryParams,
    ItemResponse,
    PaginatedItemsResponse,
    ItemAdminResponse,
    ItemUpdateRequest,
    ItemCreateRequest
)

class ItemService:
    MAX_ITEMS_LIMIT = 100

    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository

    def create_item(self, payload: ItemCreateRequest) -> ItemAdminResponse:
        existing_item = self.item_repository.get_by_name(payload.name)

        if existing_item is not None:
            raise ItemAlreadyExistsError(payload.name)
        
        if not self.item_repository.brand_exists(payload.brand_id):
            raise HTTPException(
                status_code=404,
                detail=f"Brand {payload.brand_id} not found or inactive"
            )

        if not self.item_repository.category_exists(payload.category_id):
            raise HTTPException(
                status_code=404,
                detail=f"Category {payload.category_id} not found or inactive"
            )


        item = self.item_repository.create(payload)

        item_with_relations = self.item_repository.get_by_id(item.id)

        return ItemAdminResponse.model_validate(item_with_relations)


    def get_items(
        self,
        params: ItemQueryParams
    ) -> PaginatedItemsResponse:

        allowed_sort = {
            "name",
            "price",
            "created_at"
        }

        allowed_order = {
            "asc",
            "desc"
        }

        if params.sort_by not in allowed_sort:
            params.sort_by = "created_at"

        if params.order not in allowed_order:
            params.order = "desc"

        params.limit = min(params.limit, 100)

        params.page = max(params.page, 1)

        items, total = self.item_repository.get_items_and_count(params)

        total_pages = (
            math.ceil(total / params.limit)
            if total else 1
        )

        return PaginatedItemsResponse(
            total=total,

            page=params.page,
            limit=params.limit,

            total_pages=total_pages,

            items=[
                ItemResponse.model_validate(item)
                for item in items
            ]
        )

    def get_item_by_id(self, item_id: int,current_user: User | None,) -> ItemAdminResponse | ItemResponse:

        item = self.item_repository.get_by_id(item_id)

        if item is None:
            raise ItemNotFoundError(item_id)
        
        is_admin = (
            current_user is not None and
            current_user.role == UserRole.ADMIN
        )

        if not item.is_active and not is_admin:
             raise ItemNotFoundError(item_id)
        
        if is_admin:
            return ItemAdminResponse.model_validate(item)

        return ItemResponse.model_validate(item)

    def update_item(self, item_id: int, payload: ItemUpdateRequest) -> ItemAdminResponse:
        existing_item = self.item_repository.get_by_id(item_id)

        if existing_item is None:
            raise ItemNotFoundError(item_id)
        
        if payload.name and payload.name != existing_item.name:
            if self.item_repository.get_by_name(payload.name):
                raise HTTPException(
                    status_code=400,
                    detail=f"Item with name '{payload.name}' already exists"
                )
        if payload.brand_id and payload.brand_id != existing_item.brand_id:
            if not self.item_repository.brand_exists(payload.brand_id):
                raise HTTPException(
                    status_code=404,
                    detail=f"Brand {payload.brand_id} not found or inactive"
                )
            
        if payload.category_id and payload.category_id != existing_item.category_id:
            if not self.item_repository.category_exists(payload.category_id):
                raise HTTPException(
                    status_code=404,
                    detail=f"Category {payload.category_id} not found or inactive"
                )
        updated_item = self.item_repository.update(existing_item,payload)

        item_with_relations = self.item_repository.get_by_id(updated_item.id)

        return ItemAdminResponse.model_validate(item_with_relations)

    def delete_item(self, item_id: int) -> dict:
        existing_item = self.item_repository.get_by_id(item_id)

        if existing_item is None:
            raise ItemNotFoundError(item_id)
        
        if not existing_item.is_active:
            raise HTTPException(
                status_code=400,
                detail="Item is already deleted"
            )

        self.item_repository.soft_delete(existing_item)
        return {"message": f"Item {item_id} deleted successfully"}
    
    def restore_item(self,item_id:int) -> ItemAdminResponse:
        item = self.item_repository.get_by_id(item_id)

        if item is None:
            raise ItemNotFoundError(item_id)
        
        if item.is_active:
            raise HTTPException(
                status_code=400,
                detail="Item is already active"
            )
        restored = self.item_repository.restore(item)
        return ItemAdminResponse.model_validate(restored)