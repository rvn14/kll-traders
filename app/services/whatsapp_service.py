import logging
from app.models.user import User
from app.schemas.order_schema import BillSummary

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    Placeholder service for WhatsApp integration.
    """
    
    def send_bill(self, user: User, bill: BillSummary, is_receipt: bool = False):
        """
        Sends a bill to the user via WhatsApp.
        If is_receipt is True, sends a payment confirmation receipt.
        Otherwise, sends an initial bill requesting payment.
        """
        # TODO: Implement actual WhatsApp API integration here
        message = (
            "We have received your payment. Here is your confirmed bill." 
            if is_receipt 
            else "Please make a payment for this invoice."
        )
        
        bill_type = "PAYMENT RECEIPT" if is_receipt else "INITIAL BILL"
        
        logger.info(
            f"WHATSAPP PLACEHOLDER: Sending {bill_type} to {user.full_name} ({user.phone_number}). "
            f"Invoice: {bill.invoice_no}, Total: {bill.total_amount}. "
            f"Message: '{message}'"
        )
        print(f"--> [WhatsApp] Sent {bill_type.lower()} {bill.invoice_no} to {user.phone_number}")
