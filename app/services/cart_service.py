from __future__ import annotations

from fastapi import HTTPException, status

from app.core.exceptions import ItemNotFoundError
from app.models.cart import Cart
from app.models.user import User
from app.repositories.cart_repository import CartRepository
from app.repositories.customer_profile_repository import CustomerProfileRepository
from app.repositories.item_repository import ItemRepository


class CartService:
    def __init__(
        self,
        cart_repository: CartRepository,
        customer_profile_repository: CustomerProfileRepository,
        item_repository: ItemRepository,
    ):
        self.cart_repository = cart_repository
        self.customer_profile_repository = customer_profile_repository
        self.item_repository = item_repository

    def _get_customer_profile_id(self, user: User) -> int:
        profile = self.customer_profile_repository.get_customer_profile(user.id)
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found",
            )
        return profile.id

    def _get_or_create_cart(self, user: User) -> Cart:
        customer_profile_id = self._get_customer_profile_id(user)
        return self.cart_repository.get_or_create_cart_for_customer(customer_profile_id)

    def get_cart(self, user: User) -> Cart:
        cart = self._get_or_create_cart(user)
        return self.cart_repository.get_cart_by_customer_id(cart.customer_id) or cart

    def add_to_cart(self, user: User, item_id: int, quantity: int) -> Cart:
        if quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be at least 1",
            )

        item = self.item_repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        if not getattr(item, "is_active", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item is not available",
            )

        cart = self._get_or_create_cart(user)
        return self.cart_repository.add_item(cart, item_id=item.id, quantity=quantity)

    def update_cart_item(self, user: User, item_id: int, quantity: int) -> Cart:
        if quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be at least 1",
            )

        item = self.item_repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        if not getattr(item, "is_active", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item is not available",
            )

        cart = self._get_or_create_cart(user)

        updated = self.cart_repository.update_item_quantity(cart, item_id=item.id, quantity=quantity)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item is not in cart",
            )

        return self.cart_repository.get_cart_by_customer_id(cart.customer_id) or cart

    def remove_from_cart(self, user: User, item_id: int) -> Cart:
        item = self.item_repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)

        cart = self._get_or_create_cart(user)

        removed = self.cart_repository.remove_item(cart, item_id=item.id)
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item is not in cart",
            )

        return self.cart_repository.get_cart_by_customer_id(cart.customer_id) or cart
