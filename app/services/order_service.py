from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.exceptions import (
    EmptyCartError,
    InsufficientStockError,
    InvalidOrderTypeError,
    ItemNotFoundError,
    OrderNotFoundError,
)
from app.models.address import Address
from app.models.cart_item import CartItem
from app.models.item import Item
from app.schemas.item_schema import ItemUpdateRequest
from app.models.order import Order, OrderStatus, OrderType, PaymentStatus
from app.models.order_item import OrderItem
from app.models.user import User
from app.repositories.cart_repository import CartRepository
from app.repositories.customer_profile_repository import CustomerProfileRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.settings_repository import SettingsRepository
from app.schemas.order_schema import (
    BillSummary,
    OrderItemRead,
    PaginatedOrdersResponse,
    PaginatedPurchaseHistory,
    PurchasedItemRead,
    OrderRead,
)
from app.schemas.cutomer_profile_schema import AddressRead
from app.services.whatsapp_service import WhatsAppService


@dataclass
class BillBreakdown:
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    delivery_fee: Decimal
    total_amount: Decimal


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        cart_repository: CartRepository,
        item_repository: ItemRepository,
        customer_profile_repository: CustomerProfileRepository,
        settings_repository: SettingsRepository,
        whatsapp_service: WhatsAppService,
    ):
        self.order_repository = order_repository
        self.cart_repository = cart_repository
        self.item_repository = item_repository
        self.customer_profile_repository = customer_profile_repository
        self.settings_repository = settings_repository
        self.whatsapp_service = whatsapp_service

    # Helpers

    def _get_customer_profile_id(self, user: User) -> int:
        profile = self.customer_profile_repository.get_customer_profile(user.id)
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found",
            )
        return profile.id

    def _get_address(self, address_id: int, profile_id: int) -> Address:
        address = self.customer_profile_repository.get_address_by_id(
            address_id, profile_id
        )
        if address is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )
        return address

    def _get_address_by_id_admin(self, address_id: int) -> Address:
        """Admin version: lookup address without profile constraint."""
        from sqlalchemy import select
        from app.models.address import Address as AddrModel

        db = self.order_repository.db
        stmt = select(AddrModel).where(AddrModel.id == address_id)
        addr = db.execute(stmt).scalars().first()
        if addr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )
        return addr

    def calculate_delivery_fee(self, address: Address | None) -> Decimal:
        if address is None:
            return Decimal("0")

        settings = get_settings()
        city = address.city.strip().lower()
        store_city = settings.STORE_CITY.strip().lower()
        nearby = settings.get_nearby_cities_list()

        if city == store_city:
            return Decimal(str(settings.DELIVERY_FEE_LOCAL))
        elif city in nearby:
            return Decimal(str(settings.DELIVERY_FEE_NEARBY))
        else:
            return Decimal(str(settings.DELIVERY_FEE_OTHER))

    def calculate_bill(
        self,
        items_with_qty: list[tuple[Item, int]],
        order_type: OrderType,
        address: Address | None,
    ) -> BillBreakdown:
        subtotal = Decimal("0")
        discount_amount = Decimal("0")

        for item, qty in items_with_qty:
            price = item.price
            disc = item.discount_price
            if disc is not None and disc < price:
                effective = disc
                discount_amount += (price - disc) * qty
            else:
                effective = price
            subtotal += effective * qty

        tax_rate = self.settings_repository.get_tax_rate()
        tax_amount = (subtotal * tax_rate / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        if order_type == OrderType.DELIVERY:
            delivery_fee = self.calculate_delivery_fee(address)
        else:
            delivery_fee = Decimal("0")

        total_amount = subtotal + tax_amount + delivery_fee

        return BillBreakdown(
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
        )

    def _validate_stock(self, item: Item, quantity: int) -> None:
        if item.current_stock < quantity:
            raise InsufficientStockError(
                item_name=item.name,
                available=item.current_stock,
                requested=quantity,
            )

    def _deduct_stock(self, item: Item, quantity: int) -> None:
        payload = ItemUpdateRequest(current_stock=item.current_stock - quantity)
        self.item_repository.update(item, payload)

    def _build_order_item_reads(self, order: Order) -> list[OrderItemRead]:
        reads = []
        for oi in order.order_items:
            reads.append(
                OrderItemRead(
                    id=oi.id,
                    item_id=oi.item_id,
                    item_name=oi.item.name if oi.item else "Unknown",
                    quantity=oi.quantity,
                    unit_price=oi.unit_price,
                    discount_price=oi.discount_price,
                    line_total=oi.line_total,
                )
            )
        return reads

    def _build_bill_summary(
        self, order: Order
    ) -> BillSummary:
        address_read = None
        if order.delivery_address is not None:
            address_read = AddressRead.model_validate(order.delivery_address)

        return BillSummary(
            order_id=order.id,
            invoice_no=order.invoice_no,
            order_type=order.order_type,
            order_status=order.order_status,
            payment_status=order.payment_status,
            items=self._build_order_item_reads(order),
            subtotal=order.subtotal,
            discount_amount=order.discount_amount,
            tax_amount=order.tax_amount,
            delivery_fee=order.delivery_fee,
            total_amount=order.total_amount,
            delivery_address=address_read,
            order_note=order.order_note,
            created_at=order.created_at,
        )

    def _build_order_read(self, order: Order) -> OrderRead:
        address_read = None
        if order.delivery_address is not None:
            address_read = AddressRead.model_validate(order.delivery_address)

        return OrderRead(
            id=order.id,
            invoice_no=order.invoice_no,
            customer_id=order.customer_id,
            order_type=order.order_type,
            subtotal=order.subtotal,
            discount_amount=order.discount_amount,
            tax_amount=order.tax_amount,
            delivery_fee=order.delivery_fee,
            total_amount=order.total_amount,
            payment_status=order.payment_status,
            payment_method=order.payment_method,
            order_status=order.order_status,
            delivery_date=order.delivery_date,
            order_note=order.order_note,
            delivery_address=address_read,
            order_items=self._build_order_item_reads(order),
            created_at=order.created_at,
            updated_at=order.updated_at,
        )


    # Cart Checkout

    def checkout_from_cart(
        self,
        user: User,
        order_type: OrderType,
        delivery_address_id: int | None,
        order_note: str | None,
    ) -> BillSummary:
        profile_id = self._get_customer_profile_id(user)
        cart = self.cart_repository._get_or_create_cart_for_customer(profile_id)

        # Get selected items
        selected_items = self.cart_repository.get_selected_items(cart.id)
        if not selected_items:
            raise EmptyCartError()

        # Validate delivery address for delivery orders
        address = None
        if order_type == OrderType.DELIVERY:
            if delivery_address_id is None:
                raise InvalidOrderTypeError(
                    "Delivery address is required for delivery orders."
                )
            address = self._get_address(delivery_address_id, profile_id)
        elif order_type == OrderType.PICKUP:
            delivery_address_id = None

        # Validate stock
        items_with_qty: list[tuple[Item, int]] = []
        for cart_item in selected_items:
            item = cart_item.item
            self._validate_stock(item, cart_item.quantity)
            items_with_qty.append((item, cart_item.quantity))

        # Calculate bill
        bill = self.calculate_bill(items_with_qty, order_type, address)

        # Generate invoice
        invoice_no = self.order_repository.generate_invoice_number()

        # Create order
        order = Order(
            invoice_no=invoice_no,
            customer_id=profile_id,
            order_type=order_type,
            subtotal=bill.subtotal,
            discount_amount=bill.discount_amount,
            tax_amount=bill.tax_amount,
            delivery_fee=bill.delivery_fee,
            total_amount=bill.total_amount,
            delivery_address_id=delivery_address_id,
            order_note=order_note,
            order_status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
        )

        # Create order items (snapshot prices)
        for cart_item in selected_items:
            item = cart_item.item
            effective_price = (
                item.discount_price
                if item.discount_price is not None and item.discount_price < item.price
                else item.price
            )
            order_item = OrderItem(
                item_id=item.id,
                quantity=cart_item.quantity,
                unit_price=item.price,
                discount_price=item.discount_price,
                line_total=effective_price * cart_item.quantity,
            )
            order.order_items.append(order_item)

        created_order = self.order_repository.create_order(order)

        # Deduct stock
        for cart_item in selected_items:
            self._deduct_stock(cart_item.item, cart_item.quantity)

        # Deselect checked-out items (keep them in cart but mark as unselected)
        for cart_item in selected_items:
            self.cart_repository.toggle_item_selection(
                cart.id, cart_item.item_id, False
            )

        # Cart history trimming: keep only the latest N items
        settings = get_settings()
        all_cart_items = cart.items
        if len(all_cart_items) > settings.CART_HISTORY_LIMIT:
            # Sort by added_at descending, remove oldest beyond limit
            sorted_items = sorted(all_cart_items, key=lambda ci: ci.added_at, reverse=True)
            for old_item in sorted_items[settings.CART_HISTORY_LIMIT:]:
                self.cart_repository.remove_item(cart, old_item.item_id)

        # Send initial bill via whatsapp to request payment
        bill_summary = self._build_bill_summary(created_order)
        self.whatsapp_service.send_bill(user, bill_summary)

        return bill_summary

    # Direct Buy

    def direct_buy_preview(
        self,
        user: User,
        item_id: int,
        quantity: int,
        order_type: OrderType,
        delivery_address_id: int | None = None,
        order_note: str | None = None,
    ) -> BillSummary:
        profile_id = self._get_customer_profile_id(user)

        item = self.item_repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        if not item.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item is not available",
            )
        self._validate_stock(item, quantity)

        # Validate address
        address = None
        if order_type == OrderType.DELIVERY:
            if delivery_address_id is None:
                raise InvalidOrderTypeError(
                    "Delivery address is required for delivery orders."
                )
            address = self._get_address(delivery_address_id, profile_id)

        bill = self.calculate_bill([(item, quantity)], order_type, address)

        # Build a preview (no order created yet)
        effective_price = (
            item.discount_price
            if item.discount_price is not None and item.discount_price < item.price
            else item.price
        )

        address_read = None
        if address is not None:
            address_read = AddressRead.model_validate(address)

        return BillSummary(
            order_id=0,  # not yet created
            invoice_no="PREVIEW",
            order_type=order_type,
            order_status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            items=[
                OrderItemRead(
                    id=0,
                    item_id=item.id,
                    item_name=item.name,
                    quantity=quantity,
                    unit_price=item.price,
                    discount_price=item.discount_price,
                    line_total=effective_price * quantity,
                )
            ],
            subtotal=bill.subtotal,
            discount_amount=bill.discount_amount,
            tax_amount=bill.tax_amount,
            delivery_fee=bill.delivery_fee,
            total_amount=bill.total_amount,
            delivery_address=address_read,
            order_note=order_note,
            created_at=datetime.utcnow(),
        )

    def direct_buy(
        self,
        user: User,
        item_id: int,
        quantity: int,
        order_type: OrderType,
        delivery_address_id: int | None = None,
        order_note: str | None = None,
    ) -> BillSummary:
        profile_id = self._get_customer_profile_id(user)

        item = self.item_repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        if not item.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item is not available",
            )
        self._validate_stock(item, quantity)

        # Validate address
        address = None
        if order_type == OrderType.DELIVERY:
            if delivery_address_id is None:
                raise InvalidOrderTypeError(
                    "Delivery address is required for delivery orders."
                )
            address = self._get_address(delivery_address_id, profile_id)

        bill = self.calculate_bill([(item, quantity)], order_type, address)

        invoice_no = self.order_repository.generate_invoice_number()

        effective_price = (
            item.discount_price
            if item.discount_price is not None and item.discount_price < item.price
            else item.price
        )

        order = Order(
            invoice_no=invoice_no,
            customer_id=profile_id,
            order_type=order_type,
            subtotal=bill.subtotal,
            discount_amount=bill.discount_amount,
            tax_amount=bill.tax_amount,
            delivery_fee=bill.delivery_fee,
            total_amount=bill.total_amount,
            delivery_address_id=delivery_address_id if order_type == OrderType.DELIVERY else None,
            order_note=order_note,
            order_status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
        )

        order_item = OrderItem(
            item_id=item.id,
            quantity=quantity,
            unit_price=item.price,
            discount_price=item.discount_price,
            line_total=effective_price * quantity,
        )
        order.order_items.append(order_item)

        created_order = self.order_repository.create_order(order)

        # Deduct stock
        self._deduct_stock(item, quantity)

        # Send initial bill via whatsapp
        bill_summary = self._build_bill_summary(created_order)
        self.whatsapp_service.send_bill(user, bill_summary)

        return bill_summary

    # Bill Summary

    def get_bill_summary(
        self, user: User, order_id: int, is_admin: bool = False
    ) -> BillSummary:
        order = self.order_repository.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)

        if not is_admin:
            profile_id = self._get_customer_profile_id(user)
            if order.customer_id != profile_id:
                raise OrderNotFoundError(order_id)

        return self._build_bill_summary(order)

    # List Orders (Customer)

    def get_my_orders(
        self, user: User, page: int = 1, limit: int = 20
    ) -> PaginatedOrdersResponse:
        profile_id = self._get_customer_profile_id(user)
        skip = (page - 1) * limit
        orders = self.order_repository.get_orders_by_customer(
            profile_id, skip=skip, limit=limit
        )
        total = self.order_repository.count_orders_by_customer(profile_id)
        total_pages = math.ceil(total / limit) if limit > 0 else 0

        return PaginatedOrdersResponse(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            orders=[self._build_order_read(o) for o in orders],
        )

    def get_my_order(self, user: User, order_id: int) -> OrderRead:
        order = self.order_repository.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)

        profile_id = self._get_customer_profile_id(user)
        if order.customer_id != profile_id:
            raise OrderNotFoundError(order_id)

        return self._build_order_read(order)

    # Purchase History (Individual Items)

    def get_purchase_history(
        self, user: User, page: int = 1, limit: int = 20
    ) -> PaginatedPurchaseHistory:
        profile_id = self._get_customer_profile_id(user)
        skip = (page - 1) * limit
        order_items = self.order_repository.get_purchased_items(
            profile_id, skip=skip, limit=limit
        )
        total = self.order_repository.count_purchased_items(profile_id)

        items = []
        for oi in order_items:
            image_url = None
            if oi.item and oi.item.blob:
                image_url = oi.item.blob.image_blob_url

            items.append(
                PurchasedItemRead(
                    order_item_id=oi.id,
                    item_id=oi.item_id,
                    item_name=oi.item.name if oi.item else "Unknown",
                    item_image=image_url,
                    quantity=oi.quantity,
                    unit_price=oi.unit_price,
                    discount_price=oi.discount_price,
                    line_total=oi.line_total,
                    purchased_at=oi.created_at,
                    invoice_no=oi.order.invoice_no if oi.order else "",
                )
            )

        return PaginatedPurchaseHistory(
            total=total,
            page=page,
            limit=limit,
            items=items,
        )

    # Admin Operations

    def admin_get_all_orders(
        self, page: int = 1, limit: int = 20
    ) -> PaginatedOrdersResponse:
        skip = (page - 1) * limit
        orders = self.order_repository.get_all_orders(skip=skip, limit=limit)
        total = self.order_repository.count_all_orders()
        total_pages = math.ceil(total / limit) if limit > 0 else 0

        return PaginatedOrdersResponse(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            orders=[self._build_order_read(o) for o in orders],
        )

    def admin_get_order(self, order_id: int) -> OrderRead:
        order = self.order_repository.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return self._build_order_read(order)

    def admin_update_order(
        self,
        order_id: int,
        delivery_address_id: int | None,
        order_note: str | None,
    ) -> BillSummary:
        order = self.order_repository.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)

        update_data: dict = {}

        if order_note is not None:
            update_data["order_note"] = order_note

        # If address changes, recalculate delivery fee and total
        if delivery_address_id is not None and delivery_address_id != order.delivery_address_id:
            address = self._get_address_by_id_admin(delivery_address_id)
            new_delivery_fee = self.calculate_delivery_fee(address)

            # Recalculate total: subtotal + tax stays same, delivery fee changes
            new_total = order.subtotal + order.tax_amount + new_delivery_fee

            update_data["delivery_address_id"] = delivery_address_id
            update_data["delivery_fee"] = new_delivery_fee
            update_data["total_amount"] = new_total

        if update_data:
            order = self.order_repository.update_order(order, update_data)

        return self._build_bill_summary(order)

    def admin_update_order_status(
        self,
        order_id: int,
        order_status: OrderStatus | None,
        payment_status: PaymentStatus | None,
    ) -> BillSummary:
        order = self.order_repository.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)

        update_data: dict = {}
        if order_status is not None:
            update_data["order_status"] = order_status
        if payment_status is not None:
            update_data["payment_status"] = payment_status

        if update_data:
            order = self.order_repository.update_order(order, update_data)

        bill_summary = self._build_bill_summary(order)

        # When admin confirms the payment (marks as PAID), send payment receipt bill via WhatsApp
        if payment_status == PaymentStatus.PAID:
            user = order.customer.user if (order.customer and order.customer.user) else None
            if user:
                self.whatsapp_service.send_bill(user, bill_summary, is_receipt=True)

        return bill_summary
