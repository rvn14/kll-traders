from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.item import Item


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def _get_cart_by_customer_id(self, customer_id: int) -> Cart | None:
        statement = (
            select(Cart)
            .where(Cart.customer_id == customer_id)
            .options(
                joinedload(Cart.items)
                .joinedload(CartItem.item)
                .joinedload(Item.brand),
                joinedload(Cart.items)
                .joinedload(CartItem.item)
                .joinedload(Item.category),
                joinedload(Cart.items)
                .joinedload(CartItem.item)
                .joinedload(Item.blobs),
            )
            .execution_options(populate_existing=True)
        )

        return self.db.execute(statement).unique().scalars().first()

    def _get_or_create_cart_for_customer(self, customer_id: int) -> Cart:
        try:
            existing_cart = self._get_cart_by_customer_id(customer_id)
            if existing_cart is not None:
                return existing_cart

            cart = Cart(customer_id=customer_id)
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)
            return cart
        except Exception:
            self.db.rollback()
            raise

    def get_cart_item(self, cart_id: int, item_id: int) -> CartItem | None:
        statement = select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.item_id == item_id,
        )
        return self.db.execute(statement).scalars().first()

    def add_item(self, cart: Cart, item_id: int, quantity: int) -> Cart:
        try:
            cart_item = self.get_cart_item(cart.id, item_id)

            if cart_item is None:
                cart_item = CartItem(
                    cart_id=cart.id,
                    item_id=item_id,
                    quantity=quantity,
                )
                self.db.add(cart_item)
            else:
                cart_item.quantity += quantity

            self.db.commit()

            return self._get_cart_by_customer_id(cart.customer_id) or cart
        except Exception:
            self.db.rollback()
            raise

    def update_item_quantity(self, cart: Cart, item_id: int, quantity: int) -> CartItem | None:
        try:
            cart_item = self.get_cart_item(cart.id, item_id)
            if cart_item is None:
                return None

            cart_item.quantity = quantity
            self.db.commit()
            self.db.refresh(cart_item)
            return cart_item
        except Exception:
            self.db.rollback()
            raise

    def remove_item(self, cart: Cart, item_id: int) -> bool:
        try:
            cart_item = self.get_cart_item(cart.id, item_id)
            if cart_item is None:
                return False

            self.db.delete(cart_item)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    def clear_cart(self, cart: Cart) -> None:
        try:
            cart.items.clear()
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def toggle_item_selection(self, cart_id: int, item_id: int, is_selected: bool) -> CartItem | None:
        try:
            cart_item = self.get_cart_item(cart_id, item_id)
            if cart_item is None:
                return None

            cart_item.is_selected = is_selected
            self.db.commit()
            self.db.refresh(cart_item)
            return cart_item
        except Exception:
            self.db.rollback()
            raise

    def get_selected_items(self, cart_id: int) -> list[CartItem]:
        statement = (
            select(CartItem)
            .where(CartItem.cart_id == cart_id, CartItem.is_selected == True)
            .options(
                joinedload(CartItem.item).joinedload(Item.brand),
                joinedload(CartItem.item).joinedload(Item.category),
                joinedload(CartItem.item).joinedload(Item.blobs),
            )
        )
        return list(self.db.execute(statement).unique().scalars().all())