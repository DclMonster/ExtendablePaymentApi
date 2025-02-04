from flask_restful import Resource # type: ignore
from flask import request
from ...services import PaymentProvider
from ...verifiers import google_verifier
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

class GoogleWebhookError(Exception):
    """Base exception for Google Play webhook errors."""
    pass

class GoogleWebhookData(TypedDict):
    transaction_id: str
    amount: float
    currency: str
    status: Literal['webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid']
    user_id: NotRequired[str]
    subscription_id: NotRequired[str]
    product_id: NotRequired[str]  # Product ID from Google Play
    purchase_token: NotRequired[str]  # Purchase token for verification
    package_name: NotRequired[str]  # App package name
    is_subscription: NotRequired[bool]  # Whether this is a subscription
    metadata: NotRequired[Dict[str, Any]]  # Additional metadata
    voided: NotRequired[bool]  # Whether the purchase was voided
    acknowledgement_state: NotRequired[int]  # State of purchase acknowledgement

class GoogleWebhook(Generic[ITEM_CATEGORY], AbstractWebhook[GoogleWebhookData, ITEM_CATEGORY]):
    """Resource class to handle Google Play webhook events with enhanced functionality."""
    
    def __init__(self, forwarder: Forwarder) -> None:
        """Initialize the webhook handler.
        
        Parameters
        ----------
        forwarder : Forwarder
            The forwarder for webhook events
        """
        super().__init__(
            provider_type=PaymentProvider.GOOGLE,
            verifier=google_verifier,
            forwarder=forwarder
        )

    def parse_event_data(self, event_data: str) -> GoogleWebhookData:
        """Parse the Google Play API event data.
        
        Parameters
        ----------
        event_data : str
            Raw event data from Google Play API
            
        Returns
        -------
        GoogleWebhookData
            Parsed event data
            
        Raises
        ------
        GoogleWebhookError
            If required fields are missing
        """
        try:
            data = json.loads(event_data)
            if not data:
                raise GoogleWebhookError("No JSON data in request")
                
            # Google Play API specific field mapping
            notification = data.get('message', {}).get('data', {})
            purchase = notification.get('subscriptionNotification', {}) or notification.get('oneTimeProductNotification', {})
            
            # Required fields check
            required_fields = ['orderId', 'priceAmountMicros', 'priceCurrencyCode', 'notificationType']
            missing_fields = [field for field in required_fields if field not in purchase]
            if missing_fields:
                raise GoogleWebhookError(f"Missing required fields: {', '.join(missing_fields)}")
                
            # Map Google Play API fields to our webhook data format
            status = self._map_status(purchase.get('notificationType'))
            if status not in ('webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid'):
                status = 'webhook_recieved'
                
            webhook_data: GoogleWebhookData = {
                'transaction_id': purchase['orderId'],
                'amount': float(purchase.get('priceAmountMicros', 0)) / 1_000_000,  # Convert micros to standard currency
                'currency': purchase.get('priceCurrencyCode', 'USD'),
                'status': cast(Literal['webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid'], status),
                'user_id': notification.get('userId', ''),
                'subscription_id': purchase.get('subscriptionId', ''),
                'product_id': purchase.get('productId', ''),
                'purchase_token': purchase.get('purchaseToken', ''),
                'package_name': notification.get('packageName', ''),
                'is_subscription': bool(notification.get('subscriptionNotification')),
                'metadata': notification.get('developerPayload', {}),
                'voided': False,  # Will be updated during verification
                'acknowledgement_state': purchase.get('acknowledgementState', 0)
            }
            
            # Verify purchase if we have the necessary data
            if webhook_data.get('purchase_token') and webhook_data.get('product_id'):
                try:
                    # Verify the purchase based on type
                    if webhook_data.get('is_subscription'):
                        verify_result = self._verifier.verify_subscription(
                            webhook_data['purchase_token'],
                            webhook_data['subscription_id']
                        )
                    else:
                        verify_result = self._verifier.verify_purchase(
                            webhook_data['purchase_token'],
                            webhook_data['product_id']
                        )
                    
                    # Update webhook data with verification results
                    if verify_result.get('status') == 'success':
                        webhook_data['metadata'].update({
                            'verification': verify_result,
                            'product_details': self._verifier.get_product_details(webhook_data['product_id'])
                        })
                        
                        # Check if purchase is in voided purchases list
                        voided_purchases = self._verifier.get_voided_purchases()
                        webhook_data['voided'] = any(
                            vp.get('purchaseToken') == webhook_data['purchase_token']
                            for vp in voided_purchases
                        )
                    
                    # Acknowledge the purchase if not already acknowledged
                    if not webhook_data['acknowledgement_state']:
                        self._verifier.acknowledge_purchase(
                            webhook_data['purchase_token'],
                            webhook_data['product_id'],
                            webhook_data.get('is_subscription', False)
                        )
                        
                except Exception as e:
                    webhook_data['metadata']['verification_error'] = str(e)
                    
            return webhook_data
            
        except (ValueError, KeyError) as e:
            raise GoogleWebhookError(f"Error parsing event data: {str(e)}")

    def _map_status(self, notification_type: str) -> str:
        """Map Google Play API notification type to our internal status.
        
        Parameters
        ----------
        notification_type : str
            The notification type from Google Play API
            
        Returns
        -------
        str
            Our internal status representation
        """
        if notification_type == 'SUBSCRIPTION_PURCHASED':
            return 'paid'
        elif notification_type == 'SUBSCRIPTION_RENEWED':
            return 'paid'
        elif notification_type == 'SUBSCRIPTION_CANCELED':
            return 'sent_to_processor'
        elif notification_type == 'SUBSCRIPTION_ON_HOLD':
            return 'sent_to_processor'
        elif notification_type == 'SUBSCRIPTION_IN_GRACE_PERIOD':
            return 'sent_to_processor'
        elif notification_type == 'SUBSCRIPTION_RESTARTED':
            return 'paid'
        elif notification_type == 'SUBSCRIPTION_PRICE_CHANGE_CONFIRMED':
            return 'sent_to_processor'
        elif notification_type == 'SUBSCRIPTION_DEFERRED':
            return 'sent_to_processor'
        elif notification_type == 'SUBSCRIPTION_PAUSED':
            return 'sent_to_processor'
        elif notification_type == 'SUBSCRIPTION_PAUSE_SCHEDULE_CHANGED':
            return 'sent_to_processor'
        elif notification_type == 'SUBSCRIPTION_REVOKED':
            return 'webhook_recieved'
        elif notification_type == 'SUBSCRIPTION_EXPIRED':
            return 'sent_to_processor'
        elif notification_type == 'ONE_TIME_PRODUCT_PURCHASED':
            return 'paid'
        elif notification_type == 'ONE_TIME_PRODUCT_CANCELED':
            return 'sent_to_processor'
        else:
            return 'webhook_recieved'

    def _item_name_provider(self, event_data: GoogleWebhookData) -> str:
        """Get the item name from the provider.
        
        Parameters
        ----------
        event_data : GoogleWebhookData
            The parsed event data
            
        Returns
        -------
        str
            The item name
        """
        try:
            if event_data.get('metadata', {}).get('product_details'):
                product_details = event_data['metadata']['product_details']
                return product_details.get('listing', {}).get('title', self._fallback_item_name(event_data))
            return self._fallback_item_name(event_data)
        except Exception:
            return self._fallback_item_name(event_data)

    def _fallback_item_name(self, event_data: GoogleWebhookData) -> str:
        """Fallback method for getting item name when product details are not available.
        
        Parameters
        ----------
        event_data : GoogleWebhookData
            The parsed event data
            
        Returns
        -------
        str
            The fallback item name
        """
        if event_data.get('is_subscription'):
            return f"Subscription: {event_data.get('subscription_id', '')}"
        return f"Product: {event_data.get('product_id', '')}"

    def _get_one_time_payment_data(self, event_data: GoogleWebhookData) -> OneTimePaymentData[ITEM_CATEGORY]:
        """Get one-time payment data from the event data.
        
        Parameters
        ----------
        event_data : GoogleWebhookData
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
                'purchase_token': event_data.get('purchase_token', ''),
                'package_name': event_data.get('package_name', ''),
                'voided': event_data.get('voided', False),
                'acknowledgement_state': event_data.get('acknowledgement_state', 0)
            }
        )

    def _get_subscription_payment_data(self, event_data: GoogleWebhookData) -> SubscriptionPaymentData[ITEM_CATEGORY]:
        """Get subscription payment data from the event data.
        
        Parameters
        ----------
        event_data : GoogleWebhookData
            The parsed event data
            
        Returns
        -------
        SubscriptionPaymentData
            The subscription payment data
        """
        verification_data = event_data.get('metadata', {}).get('verification', {})
        subscription_data = verification_data.get('subscription', {})
        
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
                'purchase_token': event_data.get('purchase_token', ''),
                'package_name': event_data.get('package_name', ''),
                'voided': event_data.get('voided', False),
                'acknowledgement_state': event_data.get('acknowledgement_state', 0),
                'subscription_data': subscription_data
            }
        ) 