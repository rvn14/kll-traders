from decimal import Decimal

from psycopg import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import Item


class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, item_data: dict) -> Item:
        item = Item(**item_data)

        try:
          self.db.add(item)
          self.db.commit()
          self.db.refresh(item)
          return item
        except:
          self.db.rollback()
          raise

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Item]:
        statement = (
            select(Item)
            .order_by(Item.id)
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def get_by_id(self, item_id: int) -> Item | None:
        return self.db.get(Item, item_id)
    
    def get_by_name(self, name: str) -> Item | None:
        statement = select(Item).where(Item.name == name)
        return self.db.scalars(statement).first()

    def update(self, item: Item, update_data: dict) -> Item:
        for field, value in update_data.items():
            setattr(item, field, value)

        try:
          self.db.commit()
          self.db.refresh(item)
          return item
        except IntegrityError:
          self.db.rollback()
          raise
          

    def delete(self, item: Item) -> None:
        self.db.delete(item)
        try:
          self.db.commit()
        except:
          self.db.rollback()