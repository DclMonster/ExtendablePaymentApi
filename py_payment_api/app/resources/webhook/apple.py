from flask_restful import Resource # type: ignore
from flask import request
from ...services import PaymentProvider
from ...verifiers import apple_verifier
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

class AppleWebhookError(Exception):
    """Base exception for Apple webhook errors."""
    pass

class AppleWebhookData(TypedDict):
    transaction_id: str
    amount: float
    currency: str
    status: Literal['webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid']
    user_id: NotRequired[str]
    subscription_id: NotRequired[str]
    product_id: NotRequired[str]  # Product ID from App Store
    receipt_data: NotRequired[str]  # Receipt data for verification
    bundle_id: NotRequired[str]  # App bundle ID
    is_subscription: NotRequired[bool]  # Whether this is a subscription
    metadata: NotRequired[Dict[str, Any]]  # Additional metadata
    environment: NotRequired[str]  # Sandbox or Production
    is_retryable: NotRequired[bool]  # Whether the notification can be retried

class AppleWebhook(Generic[ITEM_CATEGORY], AbstractWebhook[AppleWebhookData, ITEM_CATEGORY]):
    """Resource class to handle Apple webhook events."""
    
    def __init__(self, forwarder: Forwarder) -> None:
        """Initialize the webhook handler.
        
        Parameters
        ----------
        forwarder : Forwarder
            The forwarder for webhook events
        """
        super().__init__(
            provider_type=PaymentProvider.APPLE,
            verifier=apple_verifier,
            forwarder=forwarder
        )

    def parse_event_data(self, event_data: str) -> AppleWebhookData:
        """Parse the Apple Store API event data.
        
        Parameters
        ----------
        event_data : str
            Raw event data from Apple Store API
            
        Returns
        -------
        AppleWebhookData
            Parsed event data
            
        Raises
        ------
        AppleWebhookError
            If required fields are missing
        """
        try:
            data = json.loads(event_data)
            if not data:
                raise AppleWebhookError("No JSON data in request")
                
            # Apple Store API specific field mapping
            notification_type = data.get('notification_type')
            receipt_info = data.get('unified_receipt', {}).get('latest_receipt_info', [{}])[0]
            environment = data.get('environment', 'Production')
            
            # Required fields check
            required_fields = ['transaction_id', 'price', 'currency']
            missing_fields = [field for field in required_fields if field not in receipt_info]
            if missing_fields:
                raise AppleWebhookError(f"Missing required fields: {', '.join(missing_fields)}")
                
            # Map Apple Store API fields to our webhook data format
            status = self._map_status(notification_type, receipt_info.get('status', ''))
            if status not in ('webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid'):
                status = 'webhook_recieved'
                
            webhook_data: AppleWebhookData = {
                'transaction_id': receipt_info['transaction_id'],
                'amount': float(receipt_info.get('price', 0.0)),
                'currency': receipt_info.get('currency', 'USD'),
                'status': cast(Literal['webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid'], status),
                'user_id': data.get('user_id', ''),
                'subscription_id': receipt_info.get('product_id', ''),
                'product_id': receipt_info.get('product_id', ''),
                'receipt_data': data.get('latest_receipt', ''),
                'bundle_id': receipt_info.get('bid', ''),
                'is_subscription': bool(receipt_info.get('expires_date', '')),
                'metadata': {
                    'notification_type': notification_type,
                    'web_order_line_item_id': receipt_info.get('web_order_line_item_id', ''),
                    'is_trial_period': receipt_info.get('is_trial_period', 'false') == 'true',
                    'is_in_intro_offer_period': receipt_info.get('is_in_intro_offer_period', 'false') == 'true',
                    'original_transaction_id': receipt_info.get('original_transaction_id', ''),
                    'promotional_offer_id': receipt_info.get('promotional_offer_id', ''),
                    'offer_code_ref_name': receipt_info.get('offer_code_ref_name', '')
                },
                'environment': environment,
                'is_retryable': data.get('is-retryable', True)
            }
            
            # Verify receipt if we have the necessary data
            if webhook_data.get('receipt_data'):
                try:
                    # Verify the receipt
                    verify_result = self._verifier.verify_receipt(
                        webhook_data['receipt_data'],
                        webhook_data['environment'].lower() == 'sandbox'
                    )
                    
                    # Update webhook data with verification results
                    if verify_result.get('status') == 'success':
                        webhook_data['metadata'].update({
                            'verification': verify_result,
                            'receipt_verification': verify_result.get('receipt', {})
                        })
                        
                except Exception as e:
                    webhook_data['metadata']['verification_error'] = str(e)
                    
            return webhook_data
            
        except (ValueError, KeyError) as e:
            raise AppleWebhookError(f"Error parsing event data: {str(e)}")

    def _map_status(self, notification_type: str, status: str) -> str:
        """Map Apple Store API status to our internal status.
        
        Parameters
        ----------
        notification_type : str
            The notification type from Apple Store API
        status : str
            The status from Apple Store API
            
        Returns
        -------
        str
            Our internal status representation
        """
        if notification_type == 'INITIAL_BUY':
            return 'paid'
        elif notification_type == 'DID_RENEW':
            return 'paid'
        elif notification_type == 'INTERACTIVE_RENEWAL':
            return 'paid'
        elif notification_type == 'DID_CHANGE_RENEWAL_PREF':
            return 'sent_to_processor'
        elif notification_type == 'CANCEL':
            return 'sent_to_processor'
        elif notification_type == 'DID_CHANGE_RENEWAL_STATUS':
            return 'sent_to_processor'
        elif notification_type == 'DID_FAIL_TO_RENEW':
            return 'webhook_recieved'
        elif notification_type == 'PRICE_INCREASE_CONSENT':
            return 'sent_to_processor'
        elif notification_type == 'REFUND':
            return 'sent_to_processor'
        elif notification_type == 'REVOKE':
            return 'sent_to_processor'
        elif notification_type == 'CONSUMPTION_REQUEST':
            return 'sent_to_processor'
        else:
            return 'webhook_recieved'

    def _item_name_provider(self, event_data: AppleWebhookData) -> str:
        """Get the item name from the provider.
        
        Parameters
        ----------
        event_data : AppleWebhookData
            The parsed event data
            
        Returns
        -------
        str
            The item name
        """
        try:
            receipt_data = event_data.get('metadata', {}).get('receipt_verification', {})
            if receipt_data:
                in_app = receipt_data.get('in_app', [{}])[0]
                product_id = in_app.get('product_id', '')
                if product_id:
                    return f"Product: {product_id}"
            return self._fallback_item_name(event_data)
        except Exception:
            return self._fallback_item_name(event_data)

    def _fallback_item_name(self, event_data: AppleWebhookData) -> str:
        """Fallback method for getting item name when receipt data is not available.
        
        Parameters
        ----------
        event_data : AppleWebhookData
            The parsed event data
            
        Returns
        -------
        str
            The fallback item name
        """
        if event_data.get('is_subscription'):
            return f"Subscription: {event_data.get('subscription_id', '')}"
        return f"Product: {event_data.get('product_id', '')}"

    def _get_one_time_payment_data(self, event_data: AppleWebhookData) -> OneTimePaymentData[ITEM_CATEGORY]:
        """Get one-time payment data from the event data.
        
        Parameters
        ----------
        event_data : AppleWebhookData
            The parsed event data
            
        Returns
        -------
        OneTimePaymentData
            The one-time payment data
        """
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
                'product_id': event_data.get('product_id', ''),
                'bundle_id': event_data.get('bundle_id', ''),
                'environment': event_data.get('environment', 'Production'),
                'is_retryable': event_data.get('is_retryable', True)
            }
        )

    def _get_subscription_payment_data(self, event_data: AppleWebhookData) -> SubscriptionPaymentData[ITEM_CATEGORY]:
        """Get subscription payment data from the event data.
        
        Parameters
        ----------
        event_data : AppleWebhookData
            The parsed event data
            
        Returns
        -------
        SubscriptionPaymentData
            The subscription payment data
        """
        verification_data = event_data.get('metadata', {}).get('verification', {})
        receipt_data = verification_data.get('receipt', {})
        
        return SubscriptionPaymentData(
            user_id=event_data['user_id'],
            item_category=cast(ITEM_CATEGORY, ItemType.SUBSCRIPTION),
            purchase_id=event_data['transaction_id'],
            item_name=self._item_name_provider(event_data),
            time_bought=datetime.now().isoformat(),
            status=event_data['status'],
            metadata={
                **event_data.get('metadata', {}),
                'subscription_id': event_data.get('subscription_id', ''),
                'product_id': event_data.get('product_id', ''),
                'bundle_id': event_data.get('bundle_id', ''),
                'environment': event_data.get('environment', 'Production'),
                'is_retryable': event_data.get('is_retryable', True),
                'receipt_data': receipt_data
            }
        )
