from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException

from app.models.item import Item
from app.models.brand import Brand
from app.models.category import Category
from app.schemas.item_schema import (
    ItemQueryParams,
    ItemCreateRequest,
    ItemUpdateRequest,
)


class ItemRepository:

    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        return (
            select(Item)
            .options(
                joinedload(Item.category),
                joinedload(Item.brand),
                joinedload(Item.blob),
            )
            .where(Item.is_active == True)
        )

    def _apply_filters(self, query, params: ItemQueryParams):
        if params.search:
            term = f"%{params.search.lower()}%"
            query = query.where(
                or_(
                    func.lower(Item.name).like(term),
                    func.lower(Item.description).like(term),
                )
            )
        if params.category_id is not None:
            query = query.where(Item.category_id == params.category_id)

        if params.brand_id is not None:
            query = query.where(Item.brand_id == params.brand_id)

        if params.min_price is not None:
            query = query.where(Item.price >= params.min_price)

        if params.max_price is not None:
            query = query.where(Item.price <= params.max_price)

        if params.is_featured is not None:
            query = query.where(Item.is_featured == params.is_featured)

        if params.in_stock is True:
            query = query.where(Item.current_stock > 0)

        return query

    def _apply_sorting(self, query, params: ItemQueryParams):
        allowed_sort_fields = {
            "name":       Item.name,
            "price":      Item.price,
            "created_at": Item.created_at,
        }
        sort_column = allowed_sort_fields.get(params.sort_by, Item.created_at)

        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        return query


    def get_items_and_count(
        self,
        params: ItemQueryParams,
    ) -> tuple[list[Item], int]:
        try:
            base     = self._base_query()
            filtered = self._apply_filters(base, params)

            count_query = select(func.count()).select_from(filtered.subquery())
            total       = self.db.scalar(count_query) or 0

            sorted_query = self._apply_sorting(filtered, params)
            offset       = (params.page - 1) * params.limit
            paginated    = sorted_query.offset(offset).limit(params.limit)

            items = list(self.db.scalars(paginated).unique())

            return items, total

        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="Database error while fetching items"
            )

    def get_by_id(self, item_id: int) -> Item | None:
        try:
            return (
                self.db.query(Item)
                .options(
                    joinedload(Item.brand),
                    joinedload(Item.category),
                    joinedload(Item.blob),
                )
                .filter(Item.id == item_id)
                .first()
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="Database error while fetching item"
            )

    def get_by_name(self, name: str) -> Item | None:
        try:
            statement = select(Item).where(Item.name == name)
            return self.db.scalars(statement).first()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="Database error while checking item name"
            )

    def brand_exists(self, brand_id: int) -> bool:
        try:
            return (
                self.db.query(Brand)
                .filter(
                    Brand.id == brand_id,
                    Brand.is_active == True,
                )
                .first() is not None
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="Database error while checking brand"
            )

    def category_exists(self, category_id: int) -> bool:
        try:
            return (
                self.db.query(Category)
                .filter(
                    Category.id == category_id,
                    Category.is_active == True,
                )
                .first() is not None
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="Database error while checking category"
            )


    def create(self, payload: ItemCreateRequest) -> Item:
        item = Item(
            name           = payload.name,
            description    = payload.description,
            brand_id       = payload.brand_id,
            category_id    = payload.category_id,
            price          = payload.price,
            discount_price = payload.discount_price,
            cost_price     = payload.cost_price,
            warranty_weeks = payload.warranty_weeks,
            weight_kg      = payload.weight_kg,
            current_stock  = payload.current_stock,
            is_featured    = payload.is_featured,
            is_active      = True,
        )
        try:
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Item with this name already exists"
            )
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Database error while creating item"
            )

    def update(self, item: Item, payload: ItemUpdateRequest) -> Item:
        update_data = payload.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided to update"
            )

        for field, value in update_data.items():
            setattr(item, field, value)

        try:
            self.db.commit()
            self.db.refresh(item)
            return item

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Item with this name already exists"
            )
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Database error while updating item"
            )

    def soft_delete(self, item: Item) -> Item:
        try:
            item.is_active = False
            self.db.commit()
            self.db.refresh(item)
            return item

        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Database error while deleting item"
            )

    def restore(self, item: Item) -> Item:
        try:
            item.is_active = True
            self.db.commit()
            self.db.refresh(item)
            return item

        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Database error while restoring item"
            )
