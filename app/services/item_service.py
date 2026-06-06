from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ItemAlreadyExistsError, ItemNotFoundError
from app.models.item import Item
from app.repositories.item_repository import ItemRepository
from app.schemas.item_schema import ItemQueryParams


class ItemService:
    MAX_ITEMS_LIMIT = 100

    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository

    def create_item(self, item_data: ItemQueryParams) -> Item:
        existing_item = self.item_repository.get_by_name(item_data.name)

        if existing_item is not None:
            raise ItemAlreadyExistsError(item_data.name)

        data = item_data.model_dump()

        try:
            return self.item_repository.create(data)
        except IntegrityError:
            raise ItemAlreadyExistsError(item_data.name)

    def get_items(self, skip: int = 0, limit: int = 100) -> list[Item]:
        safe_limit = min(limit, self.MAX_ITEMS_LIMIT)
        return self.item_repository.get_all(skip=skip, limit=safe_limit)

    def get_item_by_id(self, item_id: int) -> Item:
        item = self.item_repository.get_by_id(item_id)

        if item is None:
            raise ItemNotFoundError(item_id)

        return item

    def update_item(self, item_id: int, item_data: ItemQueryParams) -> Item:
        existing_item = self.item_repository.get_by_id(item_id)

        if existing_item is None:
            raise ItemNotFoundError(item_id)

        update_data = item_data.model_dump(exclude_unset=True)

        if not update_data:
            return existing_item

        new_name = update_data.get("name")

        if new_name is not None:
            item_with_same_name = self.item_repository.get_by_name(new_name)

            if item_with_same_name is not None and item_with_same_name.id != item_id:
                raise ItemAlreadyExistsError(new_name)

        try:
            return self.item_repository.update(existing_item, update_data)
        except IntegrityError:
            if new_name is not None:
                raise ItemAlreadyExistsError(new_name)

            raise

    def attach_item_blob(
        self,
        item_id: int,
        blob_name: str,
        blob_url: str,
    ) -> Item:
        existing_item = self.item_repository.get_by_id(item_id)

        if existing_item is None:
            raise ItemNotFoundError(item_id)

        update_data = {
            "image_blob_name": blob_name,
            "image_blob_url": blob_url,
        }

        return self.item_repository.update(existing_item, update_data)

    def delete_item(self, item_id: int) -> None:
        existing_item = self.item_repository.get_by_id(item_id)

        if existing_item is None:
            raise ItemNotFoundError(item_id)

        self.item_repository.delete(existing_item)