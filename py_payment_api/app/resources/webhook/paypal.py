from flask_restful import Resource # type: ignore
from flask import request, Response
from typing import Dict, Any, Optional, NotRequired, cast, Literal, TypeVar, Generic, TypedDict, Union
from enum import StrEnum
from datetime import datetime
import json

from ...services import PaymentProvider
from ...verifiers import paypal_verifier
from ...services.forwarder.abstract.forwarder import Forwarder, ForwarderType
from ...resources.webhook.abstract.abstract_webhook import AbstractWebhook
from ...services.store.enum.item_type import ItemType
from ...services.store.payment.one_time.one_time_payment_data import OneTimePaymentData
from ...services.store.payment.subscription.subscription_payment_data import SubscriptionPaymentData


ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)

class PaypalWebhookError(Exception):
    """Base exception for PayPal webhook errors."""
    pass

class PaypalWebhookData(TypedDict):
    transaction_id: str
    amount: float
    currency: str
    status: Literal['webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid']
    user_id: NotRequired[str]
    subscription_id: NotRequired[str]


class PaypalWebhook(Generic[ITEM_CATEGORY], AbstractWebhook[PaypalWebhookData, ITEM_CATEGORY]):
    """Resource class to handle PayPal webhook events."""
    
    def __init__(self, forwarder: Forwarder) -> None:
        """Initialize the webhook handler.
        
        Parameters
        ----------
        forwarder : Forwarder
            The forwarder for webhook events
        """
        super().__init__(
            provider_type=PaymentProvider.PAYPAL,
            verifier=paypal_verifier,
            forwarder=forwarder
        )

    def parse_event_data(self, event_data: str) -> PaypalWebhookData:
        """Parse the PayPal API event data.
        
        Parameters
        ----------
        event_data : str
            Raw event data from PayPal API
            
        Returns
        -------
        PaypalWebhookData
            Parsed event data
            
        Raises
        ------
        PaypalWebhookError
            If required fields are missing
        """
        try:
            data = json.loads(event_data)
            if not data:
                raise PaypalWebhookError("No JSON data in request")
                
            # PayPal API specific field mapping
            event_type = data.get('event_type', '')
            resource = data.get('resource', {})
            amount = resource.get('amount', {})
            
            # Required fields check
            required_fields = ['id', 'amount', 'state']
            missing_fields = [field for field in required_fields if field not in resource]
            if missing_fields:
                raise PaypalWebhookError(f"Missing required fields: {', '.join(missing_fields)}")
                
            # Map PayPal API fields to our webhook data format
            status = self._map_status(event_type, resource.get('state', ''))
            if status not in ('webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid'):
                status = 'webhook_recieved'
                
            return {
                'transaction_id': resource['id'],
                'amount': float(amount.get('total', 0.0)),
                'currency': amount.get('currency', 'USD'),
                'status': cast(Literal['webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid'], status),
                'user_id': resource.get('custom_id', ''),
                'subscription_id': resource.get('billing_agreement_id', '')
            }
        except (ValueError, KeyError) as e:
            raise PaypalWebhookError(f"Error parsing event data: {str(e)}")

    def _map_status(self, event_type: str, status: str) -> str:
        """Map PayPal API status to our internal status.
        
        Parameters
        ----------
        event_type : str
            The event type from PayPal API
        status : str
            The status from PayPal API
            
        Returns
        -------
        str
            Our internal status representation
        """
        if event_type == 'PAYMENT.SALE.COMPLETED' and status == 'completed':
            return 'paid'
        elif event_type == 'PAYMENT.SALE.PENDING':
            return 'sent_to_websocket'
        elif event_type == 'PAYMENT.SALE.DENIED':
            return 'webhook_recieved'
        elif event_type == 'PAYMENT.SALE.REFUNDED':
            return 'sent_to_processor'
        elif event_type == 'BILLING.SUBSCRIPTION.CREATED':
            return 'webhook_recieved'
        elif event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
            return 'paid'
        elif event_type == 'BILLING.SUBSCRIPTION.UPDATED':
            return 'sent_to_processor'
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            return 'sent_to_processor'
        elif event_type == 'BILLING.SUBSCRIPTION.SUSPENDED':
            return 'sent_to_processor'
        elif event_type == 'BILLING.SUBSCRIPTION.EXPIRED':
            return 'sent_to_processor'
        else:
            return 'webhook_recieved'

    def _item_name_provider(self, event_data: PaypalWebhookData) -> str:
        """Get the item name from the provider.
        
        Parameters
        ----------
        event_data : PaypalWebhookData
            The parsed event data
            
        Returns
        -------
        str
            The item name
        """
        return event_data.get('subscription_id', '')

    def _get_one_time_payment_data(self, event_data: PaypalWebhookData) -> OneTimePaymentData[ITEM_CATEGORY]:
        """Get one-time payment data from the event data.
        
        Parameters
        ----------
        event_data : PaypalWebhookData
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
            quantity=1
        )

    def _get_subscription_payment_data(self, event_data: PaypalWebhookData) -> SubscriptionPaymentData[ITEM_CATEGORY]:
        """Get subscription payment data from the event data.
        
        Parameters
        ----------
        event_data : PaypalWebhookData
            The parsed event data
            
        Returns
        -------
        SubscriptionPaymentData
            The subscription payment data
        """
        return SubscriptionPaymentData(
            user_id=event_data['user_id'],
            item_category=cast(ITEM_CATEGORY, ItemType.SUBSCRIPTION),
            purchase_id=event_data['transaction_id'],
            item_name=self._item_name_provider(event_data),
            time_bought=datetime.now().isoformat(),
            status=event_data['status']
        )
