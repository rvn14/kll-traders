from __future__ import annotations

from datetime import datetime, date
from sqlalchemy import select, func as sa_func
from sqlalchemy.orm import Session, joinedload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.item import Item


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base_order_query(self):
        from app.models.user import CustomerProfile
        return (
            select(Order)
            .options(
                joinedload(Order.order_items)
                .joinedload(OrderItem.item)
                .joinedload(Item.brand),
                joinedload(Order.order_items)
                .joinedload(OrderItem.item)
                .joinedload(Item.category),
                joinedload(Order.order_items)
                .joinedload(OrderItem.item)
                .joinedload(Item.blob),
                joinedload(Order.delivery_address),
                joinedload(Order.customer).joinedload(CustomerProfile.user),
            )
        )

    def create_order(self, order: Order) -> Order:
        try:
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            return self.get_order_by_id(order.id)  # type: ignore
        except Exception:
            self.db.rollback()
            raise

    def get_order_by_id(self, order_id: int) -> Order | None:
        statement = self._base_order_query().where(Order.id == order_id)
        return self.db.execute(statement).unique().scalars().first()

    def get_order_by_invoice(self, invoice_no: str) -> Order | None:
        statement = self._base_order_query().where(Order.invoice_no == invoice_no)
        return self.db.execute(statement).unique().scalars().first()

    def get_orders_by_customer(
        self, customer_id: int, skip: int = 0, limit: int = 20
    ) -> list[Order]:
        statement = (
            self._base_order_query()
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(statement).unique().scalars().all())

    def count_orders_by_customer(self, customer_id: int) -> int:
        statement = (
            select(sa_func.count())
            .select_from(Order)
            .where(Order.customer_id == customer_id)
        )
        return self.db.execute(statement).scalar_one()

    def get_all_orders(self, skip: int = 0, limit: int = 20) -> list[Order]:
        statement = (
            self._base_order_query()
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(statement).unique().scalars().all())

    def count_all_orders(self) -> int:
        statement = select(sa_func.count()).select_from(Order)
        return self.db.execute(statement).scalar_one()

    def update_order(self, order: Order, update_data: dict) -> Order:
        try:
            for field, value in update_data.items():
                setattr(order, field, value)
            self.db.commit()
            self.db.refresh(order)
            return self.get_order_by_id(order.id)  # type: ignore
        except Exception:
            self.db.rollback()
            raise

    def generate_invoice_number(self) -> str:
        today = date.today()
        date_str = today.strftime("%Y%m%d")
        prefix = f"KLL-{date_str}-"

        # Find max invoice for today
        statement = (
            select(sa_func.max(Order.invoice_no))
            .where(Order.invoice_no.like(f"{prefix}%"))
        )
        max_invoice = self.db.execute(statement).scalar_one_or_none()

        if max_invoice is None:
            seq = 1
        else:
            # Extract the sequence number from "KLL-YYYYMMDD-XXXXX"
            try:
                seq = int(max_invoice.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:05d}"

    def get_purchased_items(
        self, customer_id: int, skip: int = 0, limit: int = 20
    ) -> list[OrderItem]:
        statement = (
            select(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .where(Order.customer_id == customer_id)
            .options(
                joinedload(OrderItem.item).joinedload(Item.brand),
                joinedload(OrderItem.item).joinedload(Item.category),
                joinedload(OrderItem.item).joinedload(Item.blob),
                joinedload(OrderItem.order),
            )
            .order_by(OrderItem.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(statement).unique().scalars().all())

    def count_purchased_items(self, customer_id: int) -> int:
        statement = (
            select(sa_func.count())
            .select_from(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .where(Order.customer_id == customer_id)
        )
        return self.db.execute(statement).scalar_one()
