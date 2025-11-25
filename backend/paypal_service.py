import os
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
import logging

logger = logging.getLogger(__name__)


class PayPalService:
    """Service for handling PayPal payments"""
    
    def __init__(self):
        self.client_id = os.environ.get('PAYPAL_CLIENT_ID', 'YOUR_PAYPAL_CLIENT_ID')
        self.secret = os.environ.get('PAYPAL_SECRET', 'YOUR_PAYPAL_SECRET')
        self.mode = os.environ.get('PAYPAL_MODE', 'sandbox')
        
        # Initialize PayPal client
        if self.mode == 'live':
            environment = LiveEnvironment(client_id=self.client_id, client_secret=self.secret)
        else:
            environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.secret)
        
        self.client = PayPalHttpClient(environment)
    
    def create_order(self, amount: float, currency: str = "GBP", description: str = "Weekly Pot Payment"):
        """
        Create a PayPal order
        Args:
            amount: Payment amount
            currency: Currency code (default: GBP)
            description: Payment description
        Returns:
            Order ID and approval URL
        """
        try:
            request = OrdersCreateRequest()
            request.prefer('return=representation')
            
            request.request_body({
                "intent": "CAPTURE",
                "purchase_units": [{
                    "description": description,
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)
                    }
                }],
                "application_context": {
                    "return_url": "http://localhost:3000/payment/success",
                    "cancel_url": "http://localhost:3000/payment/cancel"
                }
            })
            
            response = self.client.execute(request)
            
            # Extract approval URL
            approval_url = None
            for link in response.result.links:
                if link.rel == "approve":
                    approval_url = link.href
                    break
            
            return {
                "order_id": response.result.id,
                "approval_url": approval_url,
                "status": response.result.status
            }
        
        except Exception as e:
            logger.error(f"Error creating PayPal order: {str(e)}")
            return None
    
    def capture_order(self, order_id: str):
        """
        Capture/complete a PayPal order
        Args:
            order_id: PayPal order ID
        Returns:
            Capture result
        """
        try:
            request = OrdersCaptureRequest(order_id)
            response = self.client.execute(request)
            
            return {
                "order_id": response.result.id,
                "status": response.result.status,
                "payer_email": response.result.payer.email_address if hasattr(response.result.payer, 'email_address') else None,
                "amount": response.result.purchase_units[0].payments.captures[0].amount.value
            }
        
        except Exception as e:
            logger.error(f"Error capturing PayPal order: {str(e)}")
            return None
    
    def is_configured(self) -> bool:
        """Check if PayPal is properly configured"""
        return (
            self.client_id != 'YOUR_PAYPAL_CLIENT_ID' and 
            self.secret != 'YOUR_PAYPAL_SECRET'
        )
