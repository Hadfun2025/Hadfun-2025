import os
import logging
from typing import Dict, Optional
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout,
    CheckoutSessionResponse,
    CheckoutStatusResponse,
    CheckoutSessionRequest
)

logger = logging.getLogger(__name__)


class StripePaymentService:
    """Service for handling Stripe payments via emergentintegrations"""
    
    def __init__(self, api_key: str, webhook_url: str):
        """
        Initialize Stripe payment service
        
        Args:
            api_key: Stripe API key
            webhook_url: URL for Stripe webhooks
        """
        self.api_key = api_key
        self.webhook_url = webhook_url
        self.stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        logger.info(f"Stripe payment service initialized with webhook URL: {webhook_url}")
    
    async def create_pot_payment_session(
        self,
        amount: float,
        user_email: str,
        user_name: str,
        week_id: str,
        success_url: str,
        cancel_url: str
    ) -> CheckoutSessionResponse:
        """
        Create a Stripe checkout session for weekly pot contribution
        
        Args:
            amount: Payment amount in GBP (e.g., 2.0, 3.0, 5.0)
            user_email: User's email address
            user_name: User's name
            week_id: Weekly cycle identifier
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled
        
        Returns:
            CheckoutSessionResponse with url and session_id
        """
        try:
            # Metadata to track the payment
            metadata = {
                "user_email": user_email,
                "user_name": user_name,
                "week_id": week_id,
                "payment_type": "weekly_pot"
            }
            
            # Create checkout session request
            checkout_request = CheckoutSessionRequest(
                amount=float(amount),  # Ensure it's float for Stripe
                currency="gbp",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata
            )
            
            # Create the session
            session = await self.stripe_checkout.create_checkout_session(checkout_request)
            logger.info(f"Created Stripe checkout session {session.session_id} for {user_email}")
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create Stripe checkout session: {str(e)}")
            raise
    
    async def get_payment_status(self, session_id: str) -> CheckoutStatusResponse:
        """
        Get the status of a Stripe checkout session
        
        Args:
            session_id: Stripe checkout session ID
        
        Returns:
            CheckoutStatusResponse with payment status details
        """
        try:
            status = await self.stripe_checkout.get_checkout_status(session_id)
            logger.info(f"Retrieved status for session {session_id}: {status.payment_status}")
            return status
            
        except Exception as e:
            logger.error(f"Failed to get checkout status: {str(e)}")
            raise
    
    async def handle_webhook(self, webhook_body: bytes, signature: str) -> Dict:
        """
        Handle Stripe webhook events
        
        Args:
            webhook_body: Raw webhook request body
            signature: Stripe signature from headers
        
        Returns:
            Dict with webhook event details
        """
        try:
            webhook_response = await self.stripe_checkout.handle_webhook(
                webhook_body,
                signature
            )
            
            logger.info(f"Processed webhook event: {webhook_response.event_type}")
            
            return {
                "event_type": webhook_response.event_type,
                "event_id": webhook_response.event_id,
                "session_id": webhook_response.session_id,
                "payment_status": webhook_response.payment_status,
                "metadata": webhook_response.metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to handle webhook: {str(e)}")
            raise
