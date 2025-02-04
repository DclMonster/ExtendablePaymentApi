from flask_restful import Resource
from flask import request
from ...services import PaymentProvider
from ...verifiers import woocommerce_verifier
from ...services.forwarder.abstract.forwarder import Forwarder, ForwarderType
from typing import Dict, Any, Optional, NotRequired, cast, Literal, TypeVar, Generic
from typing import TypedDict
from enum import StrEnum
from ...resources.webhook.abstract.abstract_webhook import AbstractWebhook
from ...services.store.enum.item_type import ItemType
from ...services.store.payment.one_time.one_time_payment_data import OneTimePaymentData
from ...services.store.payment.subscription.subscription_payment_data import SubscriptionPaymentData
from datetime import datetime
import json

ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)

class WooCommerceWebhookError(Exception):
    """Base exception for WooCommerce webhook errors."""
    pass

class WooCommerceWebhookData(TypedDict):
    transaction_id: str
    amount: float
    currency: str
    status: Literal['webhook_received', 'sent_to_websocket', 'sent_to_processor', 'paid']
    user_id: NotRequired[str]
    order_id: NotRequired[str]
    product_id: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]
    is_subscription: NotRequired[bool]
    is_retryable: NotRequired[bool]

class WooCommerceWebhook(Generic[ITEM_CATEGORY], AbstractWebhook[WooCommerceWebhookData, ITEM_CATEGORY]):
    """Resource class to handle WooCommerce webhook events."""
    
    def __init__(self, forwarder: Forwarder) -> None:
        """Initialize the webhook handler."""
        super().__init__(
            provider_type=PaymentProvider.WOOCOMMERCE,
            verifier=woocommerce_verifier,
            forwarder=forwarder
        )

    def parse_event_data(self, event_data: str) -> WooCommerceWebhookData:
        """Parse the WooCommerce webhook event data."""
        try:
            data = json.loads(event_data)
            if not data:
                raise WooCommerceWebhookError("No JSON data in request")
                
            # Required fields check
            required_fields = ['id', 'total', 'currency']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise WooCommerceWebhookError(f"Missing required fields: {', '.join(missing_fields)}")
                
            # Map WooCommerce fields to our webhook data format
            status = self._map_status(data.get('status', ''))
            
            webhook_data: WooCommerceWebhookData = {
                'transaction_id': str(data['id']),
                'amount': float(data['total']),
                'currency': data['currency'],
                'status': cast(Literal['webhook_received', 'sent_to_websocket', 'sent_to_processor', 'paid'], status),
                'user_id': str(data.get('customer_id', '')),
                'order_id': str(data['id']),
                'product_id': str(data.get('line_items', [{}])[0].get('product_id', '')),
                'metadata': {
                    'order_key': data.get('order_key'),
                    'payment_method': data.get('payment_method'),
                    'payment_method_title': data.get('payment_method_title'),
                    'customer_note': data.get('customer_note'),
                    'created_via': data.get('created_via'),
                    'order_status': data.get('status'),
                    'webhook_event': data.get('webhook_event')
                },
                'is_subscription': any(item.get('type') == 'subscription' for item in data.get('line_items', [])),
                'is_retryable': True
            }
            
            # Verify order if we have the necessary data
            if webhook_data['order_id']:
                try:
                    verify_result = self._verifier.verify_order(
                        webhook_data['order_id'],
                        webhook_data.get('metadata', {}).get('order_key')
                    )
                    
                    if verify_result['status'] == 'success':
                        webhook_data['metadata'].update({
                            'verification': verify_result,
                            'order_verification': verify_result['order']
                        })
                except Exception as e:
                    webhook_data['metadata']['verification_error'] = str(e)
            
            return webhook_data
            
        except Exception as e:
            raise WooCommerceWebhookError(f"Error parsing webhook data: {str(e)}")

    def _map_status(self, woo_status: str) -> str:
        """Map WooCommerce status to internal status."""
        status_map = {
            'completed': 'paid',
            'processing': 'sent_to_processor',
            'pending': 'webhook_received'
        }
        return status_map.get(woo_status, 'webhook_received')

    def _get_one_time_payment_data(self, event_data: WooCommerceWebhookData) -> OneTimePaymentData[ITEM_CATEGORY]:
        """Get one-time payment data from the event data."""
        return OneTimePaymentData(
            user_id=event_data['user_id'],
            item_category=cast(ITEM_CATEGORY, ItemType.ONE_TIME_PAYMENT),
            purchase_id=event_data['transaction_id'],
            item_name=self._item_name_provider(event_data),
            time_bought=datetime.now().isoformat(),
            status=event_data['status'],
            quantity=1,
            metadata={
                **event_data.get('metadata', {}),
                'product_id': event_data.get('product_id'),
                'order_id': event_data.get('order_id'),
                'is_retryable': event_data.get('is_retryable', True)
            }
        )

    def _get_subscription_payment_data(self, event_data: WooCommerceWebhookData) -> SubscriptionPaymentData[ITEM_CATEGORY]:
        """Get subscription payment data from the event data."""
        return SubscriptionPaymentData(
            user_id=event_data['user_id'],
            item_category=cast(ITEM_CATEGORY, ItemType.SUBSCRIPTION),
            purchase_id=event_data['transaction_id'],
            item_name=self._item_name_provider(event_data),
            time_bought=datetime.now().isoformat(),
            status=event_data['status'],
            metadata={
                **event_data.get('metadata', {}),
                'product_id': event_data.get('product_id'),
                'order_id': event_data.get('order_id'),
                'is_retryable': event_data.get('is_retryable', True)
            }
        )

    def _item_name_provider(self, event_data: WooCommerceWebhookData) -> str:
        """Get the item name from the event data."""
        try:
            order_data = event_data.get('metadata', {}).get('order_verification', {})
            if order_data:
                line_items = order_data.get('line_items', [{}])
                if line_items and line_items[0].get('name'):
                    return f"Product: {line_items[0]['name']}"
            return self._fallback_item_name(event_data)
        except Exception:
            return self._fallback_item_name(event_data)

    def _fallback_item_name(self, event_data: WooCommerceWebhookData) -> str:
        """Fallback method for getting item name."""
        if event_data.get('is_subscription'):
            return f"Subscription: {event_data.get('product_id', '')}"
        return f"Product: {event_data.get('product_id', '')}" 