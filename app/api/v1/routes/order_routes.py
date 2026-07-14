from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.admin import require_admin
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_order_service
from app.models.user import User
from app.schemas.order_schema import (
    AdminOrderStatusUpdate,
    AdminOrderUpdateRequest,
    BillSummary,
    CheckoutFromCartRequest,
    DirectBuyRequest,
    OrderRead,
    PaginatedOrdersResponse,
    PaginatedPurchaseHistory,
)
from app.services.order_service import OrderService

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)

admin_router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin - Orders"],
)


# Customer Endpoints


@router.post(
    "/checkout/cart",
    response_model=BillSummary,
    status_code=status.HTTP_201_CREATED,
)
def checkout_from_cart(
    payload: CheckoutFromCartRequest,
    order_service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Checkout selected cart items → creates order, returns bill."""
    return order_service.checkout_from_cart(
        user=current_user,
        order_type=payload.order_type,
        delivery_address_id=payload.delivery_address_id,
        order_note=payload.order_note,
    )


@router.post(
    "/checkout/direct/preview",
    response_model=BillSummary,
    status_code=status.HTTP_200_OK,
)
def direct_buy_preview(
    payload: DirectBuyRequest,
    order_service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Direct buy preview → returns bill summary + confirmation token."""
    return order_service.direct_buy_preview(
        user=current_user,
        item_id=payload.item_id,
        quantity=payload.quantity,
        order_type=payload.order_type,
        delivery_address_id=payload.delivery_address_id,
        order_note=payload.order_note,
    )


@router.post(
    "/checkout/direct",
    response_model=BillSummary,
    status_code=status.HTTP_201_CREATED,
)
def direct_buy(
    payload: DirectBuyRequest,
    order_service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Confirm direct buy → creates order."""
    return order_service.direct_buy(
        user=current_user,
        item_id=payload.item_id,
        quantity=payload.quantity,
        order_type=payload.order_type,
        delivery_address_id=payload.delivery_address_id,
        order_note=payload.order_note,
    )


@router.get(
    "",
    response_model=PaginatedOrdersResponse,
    status_code=status.HTTP_200_OK,
)
def get_my_orders(
    order_service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    """List my orders (paginated)."""
    return order_service.get_my_orders(
        user=current_user,
        page=page,
        limit=limit,
    )


@router.get(
    "/history/items",
    response_model=PaginatedPurchaseHistory,
    status_code=status.HTTP_200_OK,
)
def get_purchase_history(
    order_service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Paginated list of individually purchased items."""
    return order_service.get_purchase_history(
        user=current_user,
        page=page,
        limit=limit,
    )


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
)
def get_my_order(
    order_id: int,
    order_service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get order detail (customer's own order)."""
    return order_service.get_my_order(
        user=current_user,
        order_id=order_id,
    )


@router.get(
    "/{order_id}/bill",
    response_model=BillSummary,
    status_code=status.HTTP_200_OK,
)
def get_bill_summary(
    order_id: int,
    order_service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get bill summary for an order."""
    return order_service.get_bill_summary(
        user=current_user,
        order_id=order_id,
    )


# Admin Endpoints


@admin_router.get(
    "",
    response_model=PaginatedOrdersResponse,
    status_code=status.HTTP_200_OK,
)
def admin_get_all_orders(
    order_service: Annotated[OrderService, Depends(get_order_service)],
    _admin: Annotated[User, Depends(require_admin)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    """List all orders (admin)."""
    return order_service.admin_get_all_orders(page=page, limit=limit)


@admin_router.get(
    "/{order_id}",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
)
def admin_get_order(
    order_id: int,
    order_service: Annotated[OrderService, Depends(get_order_service)],
    _admin: Annotated[User, Depends(require_admin)],
):
    """Get any order detail (admin)."""
    return order_service.admin_get_order(order_id=order_id)


@admin_router.patch(
    "/{order_id}",
    response_model=BillSummary,
    status_code=status.HTTP_200_OK,
)
def admin_update_order(
    order_id: int,
    payload: AdminOrderUpdateRequest,
    order_service: Annotated[OrderService, Depends(get_order_service)],
    _admin: Annotated[User, Depends(require_admin)],
):
    """Update order (change delivery address → recalculate fees)."""
    return order_service.admin_update_order(
        order_id=order_id,
        delivery_address_id=payload.delivery_address_id,
        order_note=payload.order_note,
    )


@admin_router.patch(
    "/{order_id}/status",
    response_model=BillSummary,
    status_code=status.HTTP_200_OK,
)
def admin_update_order_status(
    order_id: int,
    payload: AdminOrderStatusUpdate,
    order_service: Annotated[OrderService, Depends(get_order_service)],
    _admin: Annotated[User, Depends(require_admin)],
):
    """Update order/payment status. When confirmed send via whatsapp."""
    return order_service.admin_update_order_status(
        order_id=order_id,
        order_status=payload.order_status,
        payment_status=payload.payment_status,
    )
