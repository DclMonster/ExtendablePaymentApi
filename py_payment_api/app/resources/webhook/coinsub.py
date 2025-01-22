from flask_restful import Resource # type: ignore
from flask import request
from ...services import PaymentProvider
from ...verifiers import coinsub_verifier
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

class CoinSubWebhookError(Exception):
    """Base exception for CoinSub webhook errors."""
    pass

class CoinSubWebhookData(TypedDict):
    transaction_id: str
    amount: float
    currency: str
    status: Literal['webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid']
    user_id: NotRequired[str]
    subscription_id: NotRequired[str]

class CoinSubWebhook(Generic[ITEM_CATEGORY], AbstractWebhook[CoinSubWebhookData, ITEM_CATEGORY]):
    """Resource class to handle CoinSub webhook events."""
    
    def __init__(self, forwarder: Forwarder) -> None:
        """Initialize the webhook handler.
        
        Parameters
        ----------
        forwarder : Forwarder
            The forwarder for webhook events
        """
        super().__init__(
            provider_type=PaymentProvider.COINSUB,
            verifier=coinsub_verifier,
            forwarder=forwarder
        )

    def parse_event_data(self, event_data: str) -> CoinSubWebhookData:
        """Parse the CoinSub API event data.
        
        Parameters
        ----------
        event_data : str
            Raw event data from CoinSub API
            
        Returns
        -------
        CoinSubWebhookData
            Parsed event data
            
        Raises
        ------
        CoinSubWebhookError
            If required fields are missing
        """
        try:
            data = json.loads(event_data)
            if not data:
                raise CoinSubWebhookError("No JSON data in request")
                
            # CoinSub API specific field mapping
            event_type = data.get('event_type')
            subscription = data.get('subscription', {})
            
            # Required fields check
            required_fields = ['transaction_id', 'amount', 'currency', 'status']
            missing_fields = [field for field in required_fields if field not in subscription]
            if missing_fields:
                raise CoinSubWebhookError(f"Missing required fields: {', '.join(missing_fields)}")
                
            # Map CoinSub API fields to our webhook data format
            status = self._map_status(event_type, subscription.get('status'))
            if status not in ('webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid'):
                status = 'webhook_recieved'
                
            return {
                'transaction_id': subscription['transaction_id'],
                'amount': float(subscription.get('amount', 0.0)),
                'currency': subscription.get('currency', 'USD'),
                'status': cast(Literal['webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid'], status),
                'user_id': subscription.get('user_id', ''),
                'subscription_id': subscription.get('subscription_id', '')
            }
        except (ValueError, KeyError) as e:
            raise CoinSubWebhookError(f"Error parsing event data: {str(e)}")

    def _map_status(self, event_type: str, status: str) -> str:
        """Map CoinSub API status to our internal status.
        
        Parameters
        ----------
        event_type : str
            The event type from CoinSub API
        status : str
            The status from CoinSub API
            
        Returns
        -------
        str
            Our internal status representation
        """
        if event_type == 'subscription_created':
            return 'webhook_recieved'
        elif event_type == 'subscription_activated':
            return 'paid'
        elif event_type == 'subscription_canceled':
            return 'sent_to_processor'
        elif event_type == 'subscription_renewed':
            return 'paid'
        elif event_type == 'subscription_failed':
            return 'webhook_recieved'
        elif event_type == 'subscription_expired':
            return 'sent_to_processor'
        else:
            return 'webhook_recieved'

    def _item_name_provider(self, event_data: CoinSubWebhookData) -> str:
        """Get the item name from the provider.
        
        Parameters
        ----------
        event_data : CoinSubWebhookData
            The parsed event data
            
        Returns
        -------
        str
            The item name
        """
        return event_data.get('subscription_id', '')

    def _get_one_time_payment_data(self, event_data: CoinSubWebhookData) -> OneTimePaymentData[ITEM_CATEGORY]:
        """Get one-time payment data from the event data.
        
        Parameters
        ----------
        event_data : CoinSubWebhookData
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

    def _get_subscription_payment_data(self, event_data: CoinSubWebhookData) -> SubscriptionPaymentData[ITEM_CATEGORY]:
        """Get subscription payment data from the event data.
        
        Parameters
        ----------
        event_data : CoinSubWebhookData
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