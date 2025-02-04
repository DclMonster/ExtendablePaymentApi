"""WooCommerce webhook signature verifier."""
import hmac
import hashlib
import requests
import os
from typing import Dict, Any, Optional
from .abstract.signature_verifier import SignatureVerifier
from services.logger import logger

class WooCommerceVerificationError(Exception):
    """Base exception for WooCommerce verification errors."""
    pass

class WooCommerceVerifier(SignatureVerifier):
    """
    Verifier class for WooCommerce webhook signatures and API integration.
    
    This class handles all WooCommerce-related webhook verification and API requests.
    
    API Docs: https://woocommerce.github.io/woocommerce-rest-api-docs/
    """
    
    def __init__(self) -> None:
        """
        Initialize the verifier with configuration from environment variables.
        
        Required environment variables:
        - WOOCOMMERCE_WEBHOOK_SECRET: The webhook shared secret for signature verification
        - WOOCOMMERCE_CONSUMER_KEY: The consumer key for API authentication
        - WOOCOMMERCE_CONSUMER_SECRET: The consumer secret for API authentication
        - WOOCOMMERCE_API_URL: The WooCommerce store URL
        """
        super().__init__('WOOCOMMERCE_WEBHOOK_SECRET')
        
        self._consumer_key = os.getenv('WOOCOMMERCE_CONSUMER_KEY')
        self._consumer_secret = os.getenv('WOOCOMMERCE_CONSUMER_SECRET')
        self._api_url = os.getenv('WOOCOMMERCE_API_URL')
        
        if not all([self._consumer_key, self._consumer_secret, self._api_url]):
            raise ValueError("Missing required WooCommerce configuration")

    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """
        Verify the webhook signature using HMAC-SHA256.
        
        Parameters
        ----------
        data : Dict[str, Any]
            The webhook payload
        signature : str
            The signature to verify
            
        Returns
        -------
        bool
            True if signature is valid, False otherwise
        """
        try:
            # Create HMAC signature using webhook secret
            payload = str(data).encode('utf-8')
            computed = hmac.new(
                self._secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Use constant-time comparison
            return hmac.compare_digest(computed, signature)
        except Exception as e:
            logger.error(f"WooCommerce signature verification error: {str(e)}")
            return False

    def get_signature_from_header(self, header: Dict[str, Any]) -> str:
        """
        Extract the signature from the header.
        
        Parameters
        ----------
        header : Dict[str, Any]
            The header containing the signature
            
        Returns
        -------
        str
            The extracted signature
            
        Raises
        ------
        ValueError
            If signature is missing or invalid
        """
        signature = header.get('X-WC-Webhook-Signature')
        if not signature:
            raise ValueError("Missing WooCommerce signature in headers")
        if not isinstance(signature, str):
            raise ValueError("Invalid WooCommerce signature format")
        return signature

    def verify_order(self, order_id: str, order_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify an order using the WooCommerce REST API.
        
        Parameters
        ----------
        order_id : str
            The order ID to verify
        order_key : str, optional
            The order key for additional verification
            
        Returns
        -------
        Dict[str, Any]
            The verification result containing order details
            
        Raises
        ------
        WooCommerceVerificationError
            If verification fails
        """
        try:
            # Build API endpoint URL
            endpoint = f"{self._api_url}/wp-json/wc/v3/orders/{order_id}"
            
            # Add order key if provided
            params = {}
            if order_key:
                params['order_key'] = order_key
            
            # Make API request with authentication
            response = requests.get(
                endpoint,
                auth=(self._consumer_key, self._consumer_secret),
                params=params
            )
            
            if response.status_code != 200:
                raise WooCommerceVerificationError(
                    f"Order verification failed: {response.text}"
                )
            
            return {
                'status': 'success',
                'order': response.json()
            }
            
        except Exception as e:
            logger.error(f"WooCommerce order verification error: {str(e)}")
            return {
                'status': 'error',
                'error': {
                    'msg': str(e)
                }
            }

    def verify_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Verify a subscription using the WooCommerce Subscriptions API.
        
        Parameters
        ----------
        subscription_id : str
            The subscription ID to verify
            
        Returns
        -------
        Dict[str, Any]
            The verification result containing subscription details
            
        Raises
        ------
        WooCommerceVerificationError
            If verification fails
        """
        try:
            endpoint = f"{self._api_url}/wp-json/wc/v3/subscriptions/{subscription_id}"
            
            response = requests.get(
                endpoint,
                auth=(self._consumer_key, self._consumer_secret)
            )
            
            if response.status_code != 200:
                raise WooCommerceVerificationError(
                    f"Subscription verification failed: {response.text}"
                )
            
            return {
                'status': 'success',
                'subscription': response.json()
            }
            
        except Exception as e:
            logger.error(f"WooCommerce subscription verification error: {str(e)}")
            return {
                'status': 'error',
                'error': {
                    'msg': str(e)
                }
            }

    def handle_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle different types of WooCommerce webhook notifications.
        
        Parameters
        ----------
        payload : Dict[str, Any]
            The webhook payload
            
        Returns
        -------
        Dict[str, Any]
            The processed notification result
        """
        try:
            event = payload.get('webhook_event')
            
            if event in ['order.created', 'order.updated']:
                return self._handle_order_notification(payload)
            elif event in ['subscription.created', 'subscription.renewed']:
                return self._handle_subscription_notification(payload)
            elif event == 'subscription.cancelled':
                return self._handle_subscription_cancellation(payload)
            
            return {
                'status': 'error',
                'type': 'unknown_event',
                'update_body': {},
                'identifier': None
            }
            
        except Exception as e:
            logger.error(f"WooCommerce notification handling error: {str(e)}")
            return {
                'status': 'error',
                'type': 'processing_error',
                'update_body': {'error': str(e)},
                'identifier': None
            }

    def _handle_order_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order-related notifications."""
        return {
            'status': 'action_update',
            'type': 'order_update',
            'update_body': {
                'status': payload.get('status'),
                'order_id': payload.get('id')
            },
            'identifier': {
                'order_id': payload.get('id'),
                'product_id': payload.get('line_items', [{}])[0].get('product_id')
            }
        }

    def _handle_subscription_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription-related notifications."""
        return {
            'status': 'action_update',
            'type': 'subscription_update',
            'update_body': {
                'status': 'active',
                'subscription_id': payload.get('id')
            },
            'identifier': {
                'subscription_id': payload.get('id'),
                'product_id': payload.get('line_items', [{}])[0].get('product_id')
            }
        }

    def _handle_subscription_cancellation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription cancellation notifications."""
        return {
            'status': 'action_update',
            'type': 'subscription_cancelled',
            'update_body': {
                'status': 'cancelled',
                'subscription_id': payload.get('id')
            },
            'identifier': {
                'subscription_id': payload.get('id'),
                'product_id': payload.get('line_items', [{}])[0].get('product_id')
            }
        } 