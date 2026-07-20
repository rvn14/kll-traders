"""
WhatsApp Business Cloud API integration service.

Sends order bills and payment receipts to customers via
Meta WhatsApp Template Messages only.

Templates required on Meta:
    • order_payment_request  — sent when order is created
    • payment_confirmed      — sent when admin marks payment as PAID
"""

from __future__ import annotations

import logging
import re
from decimal import Decimal
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.order import OrderType
from app.models.user import User
from app.schemas.order_schema import BillSummary

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Send order bills and payment receipts via WhatsApp templates."""

    # ── Template names (must match exactly what you named in Meta) ────────
    TEMPLATE_ORDER_PAYMENT_REQUEST = "order_payment_request"
    TEMPLATE_PAYMENT_CONFIRMED     = "payment_confirmed"

    # ─────────────────────────────────────────────────────────────────────
    #  Construction
    # ─────────────────────────────────────────────────────────────────────

    def __init__(self) -> None:
        settings = get_settings()
        self._access_token:    str = settings.WHATSAPP_ACCESS_TOKEN
        self._phone_number_id: str = settings.WHATSAPP_PHONE_NUMBER_ID
        self._api_version:     str = settings.WHATSAPP_API_VERSION

        self._base_url: str = (
            f"https://graph.facebook.com/{self._api_version}"
            f"/{self._phone_number_id}/messages"
        )

    # ─────────────────────────────────────────────────────────────────────
    #  Public API
    # ─────────────────────────────────────────────────────────────────────

    def send_bill(
        self,
        user: User,
        bill_summary: BillSummary,
        is_receipt: bool = False,
    ) -> bool:
        """Send order payment request or payment confirmed message.

        Args:
            user:         Customer — must have full_name and phone_number.
            bill_summary: Full order/bill data.
            is_receipt:   False → payment request, True → payment confirmed.

        Returns:
            True on success, False on any failure (never raises).
        """
        try:
            phone = self._format_phone_number(user.phone_number)

            if phone is None:
                logger.warning(
                    "WhatsApp send skipped — invalid phone for user '%s'",
                    user.full_name,
                )
                return False

            if is_receipt:
                payload = self._build_payment_confirmed_payload(
                    phone, user, bill_summary
                )
            else:
                payload = self._build_order_payment_request_payload(
                    phone, user, bill_summary
                )

            success = self._send_request(payload)

            if success:
                self._log_success(phone, bill_summary.invoice_no, is_receipt)
            else:
                self._log_failure(
                    phone,
                    bill_summary.invoice_no,
                    is_receipt,
                    reason="API returned non-success status",
                )

            return success

        except Exception as exc:
            self._log_failure(
                getattr(user, "phone_number", "unknown"),
                getattr(bill_summary, "invoice_no", "unknown"),
                is_receipt,
                reason=str(exc),
            )
            return False

    # ─────────────────────────────────────────────────────────────────────
    #  Template payload builders
    # ─────────────────────────────────────────────────────────────────────

    def _build_order_payment_request_payload(
        self,
        phone: str,
        user: User,
        bill: BillSummary,
    ) -> dict[str, Any]:
        """Build payload for order_payment_request template.

        Variables sent (matches {{1}} … {{9}} in the template):
            1  customer name
            2  invoice number
            3  items list
            4  subtotal
            5  discount amount
            6  tax amount
            7  delivery fee
            8  total amount
            9  delivery address or pickup text
        """
        items_text    = self._format_items_list(bill)
        address_text  = self._format_address(bill)

        parameters = [
            self._text_param(user.full_name),
            self._text_param(bill.invoice_no),
            self._text_param(items_text),
            self._text_param(self._fmt(bill.subtotal)),
            self._text_param(self._fmt(bill.discount_amount)),
            # self._text_param(self._fmt(bill.tax_amount)),
            self._text_param(self._fmt(bill.delivery_fee)),
            self._text_param(self._fmt(bill.total_amount)),
            # self._text_param(address_text),
        ]

        return self._build_template_payload(
            phone,
            template_name = self.TEMPLATE_ORDER_PAYMENT_REQUEST,
            parameters    = parameters,
        )

    def _build_payment_confirmed_payload(
        self,
        phone: str,
        user: User,
        bill: BillSummary,
    ) -> dict[str, Any]:
        """Build payload for payment_confirmed template.

        Variables sent (matches {{1}} {{2}} {{3}} in the template):
            1  customer name
            2  invoice number
            3  total amount paid
        """
        parameters = [
            self._text_param(user.full_name),
            self._text_param(bill.invoice_no),
            self._text_param(self._fmt(bill.total_amount)),
        ]

        return self._build_template_payload(
            phone,
            template_name = self.TEMPLATE_PAYMENT_CONFIRMED,
            parameters    = parameters,
        )

    @staticmethod
    def _build_template_payload(
        phone: str,
        template_name: str,
        parameters: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Build the Meta template message payload structure."""
        return {
            "messaging_product": "whatsapp",
            "to":                phone,
            "type":              "template",
            "template": {
                "name":     template_name,
                "language": {"code": "en"},
                "components": [
                    {
                        "type":       "body",
                        "parameters": parameters,
                    }
                ],
            },
        }

    # ─────────────────────────────────────────────────────────────────────
    #  Formatting helpers
    # ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _text_param(value: str) -> dict[str, str]:
        """Build a single text parameter dict for a template component."""
        return {"type": "text", "text": value}

    @staticmethod
    def _fmt(amount: Decimal | float | int) -> str:
        """Format a monetary amount as 'LKR 150,500.47'."""
        value     = Decimal(str(amount)).quantize(Decimal("0.01"))
        formatted = f"{value:,.2f}"
        return f"LKR {formatted}"

    @staticmethod
    def _format_items_list(bill: BillSummary) -> str:
        """Format the ordered items as a readable text block."""
        lines = []
        for item in bill.items:
            price = Decimal(str(item.unit_price)).quantize(Decimal("0.01"))
            total = Decimal(str(item.line_total)).quantize(Decimal("0.01"))
            lines.append(
                f"• {item.item_name}\n"
                f"  Qty: {item.quantity} × LKR {price:,.2f}\n"
                f"  Total: LKR {total:,.2f}"
            )
        return "\n".join(lines)

    @staticmethod
    def _format_address(bill: BillSummary) -> str:
        """Return delivery address block or pickup text."""
        if bill.order_type == OrderType.DELIVERY and bill.delivery_address:
            addr  = bill.delivery_address
            parts = [f"📍 Delivery to: {addr.address_line_1}"]
            if addr.address_line_2:
                parts.append(addr.address_line_2)
            parts.append(f"{addr.city}, {addr.postal_code}")
            return "\n".join(parts)
        return "🏪 Pickup from store"

    # ─────────────────────────────────────────────────────────────────────
    #  Phone number formatting
    # ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _format_phone_number(raw: str | None) -> str | None:
        """Normalise a Sri-Lankan phone number to 94XXXXXXXXX.

        Accepted inputs:
            0767801583   →  94767801583
            94767801583  →  94767801583
            +94767801583 →  94767801583

        Returns None when the number is missing or invalid.
        """
        if not raw:
            return None

        digits = re.sub(r"\D", "", raw)        # strip all non-digits

        if digits.startswith("0") and len(digits) == 10:
            digits = "94" + digits[1:]         # 0767801583 → 94767801583
        elif digits.startswith("94") and len(digits) == 11:
            pass                               # already correct
        else:
            return None                        # anything else is invalid

        return digits

    # ─────────────────────────────────────────────────────────────────────
    #  HTTP transport
    # ─────────────────────────────────────────────────────────────────────

    def _send_request(self, payload: dict[str, Any]) -> bool:
        """POST payload to the Meta WhatsApp Messages API.

        Returns True on HTTP 200/201, False otherwise. Never raises.
        """
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type":  "application/json",
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(
                    self._base_url,
                    headers = headers,
                    json    = payload,
                )

            if response.status_code in (200, 201):
                return True

            logger.error(
                "WhatsApp API error — status=%s  body=%s",
                response.status_code,
                response.text,
            )
            return False

        except httpx.TimeoutException:
            logger.error("WhatsApp API request timed out (15s)")
            return False

        except httpx.HTTPError as exc:
            logger.error("WhatsApp network error: %s", exc)
            return False

    # ─────────────────────────────────────────────────────────────────────
    #  Logging helpers
    # ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _log_success(phone: str, invoice_no: str, is_receipt: bool) -> None:
        msg_type = "PAYMENT_CONFIRMED" if is_receipt else "ORDER_PAYMENT_REQUEST"
        logger.info(
            "WhatsApp %s sent | phone=%s invoice=%s",
            msg_type, phone, invoice_no,
        )

    @staticmethod
    def _log_failure(
        phone: str,
        invoice_no: str,
        is_receipt: bool,
        *,
        reason: str = "",
    ) -> None:
        msg_type = "PAYMENT_CONFIRMED" if is_receipt else "ORDER_PAYMENT_REQUEST"
        logger.error(
            "WhatsApp %s FAILED | phone=%s invoice=%s reason=%s",
            msg_type, phone, invoice_no, reason,
        )