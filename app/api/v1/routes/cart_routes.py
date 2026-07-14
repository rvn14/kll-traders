from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_cart_service
from app.models.user import User
from app.schemas.cart_schema import CartItemAdd, CartItemSelect, CartItemUpdate, CartRead
from app.services.cart_service import CartService


router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


# get my cart
@router.get(
    "",
    response_model=CartRead,
    status_code=status.HTTP_200_OK,
)
def get_my_cart(
    cart_service: Annotated[CartService, Depends(get_cart_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return cart_service.get_cart(user=current_user)


# add to cart
@router.post(
    "/items",
    response_model=CartRead,
    status_code=status.HTTP_200_OK,
)
def add_to_cart(
    payload: CartItemAdd,
    cart_service: Annotated[CartService, Depends(get_cart_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return cart_service.add_to_cart(
        user=current_user,
        item_id=payload.item_id,
        quantity=payload.quantity,
    )


# update cart item
@router.patch(
    "/items/{item_id}",
    response_model=CartRead,
)
def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    cart_service: Annotated[CartService, Depends(get_cart_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return cart_service.update_cart_item(
        user=current_user,
        item_id=item_id,
        quantity=payload.quantity,
    )


# remove cart item
@router.delete(
    "/items/{item_id}",
    response_model=CartRead,
)
def remove_cart_item(
    item_id: int,
    cart_service: Annotated[CartService, Depends(get_cart_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return cart_service.remove_from_cart(
        user=current_user,
        item_id=item_id,
    )


# clear cart
@router.delete(
    "",
    response_model=CartRead,
)
def clear_cart(
    cart_service: Annotated[CartService, Depends(get_cart_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return cart_service.clear_cart(
        user=current_user,
    )


# toggle item selection
@router.patch(
    "/items/{item_id}/select",
    response_model=CartRead,
)
def toggle_item_selection(
    item_id: int,
    payload: CartItemSelect,
    cart_service: Annotated[CartService, Depends(get_cart_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return cart_service.toggle_item_selection(
        user=current_user,
        item_id=item_id,
        is_selected=payload.is_selected,
    )