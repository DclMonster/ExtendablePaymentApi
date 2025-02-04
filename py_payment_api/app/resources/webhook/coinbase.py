"""Coinbase Commerce webhook handler."""
from flask_restful import Resource # type: ignore
from flask import request
from ...services import PaymentProvider
from ...verifiers import coinbase_verifier
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

class CoinbaseWebhookError(Exception):
    """Base exception for Coinbase webhook errors."""
    pass

class CoinbaseWebhookData(TypedDict):
    transaction_id: str
    amount: float
    currency: str
    status: Literal['webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid']
    user_id: NotRequired[str]
    subscription_id: NotRequired[str]
    charge_code: NotRequired[str]  # Coinbase Commerce charge code
    payment_method: NotRequired[str]  # Payment method used (crypto currency)
    confirmed_at: NotRequired[str]  # Confirmation timestamp

class CoinbaseWebhook(Generic[ITEM_CATEGORY], AbstractWebhook[CoinbaseWebhookData, ITEM_CATEGORY]):
    """Resource class to handle Coinbase Commerce webhook events."""
    
    def __init__(self, forwarder: Forwarder) -> None:
        """Initialize the webhook handler.
        
        Parameters
        ----------
        forwarder : Forwarder
            The forwarder for webhook events
        """
        super().__init__(
            provider_type=PaymentProvider.COINBASE,
            verifier=coinbase_verifier,
            forwarder=forwarder
        )

    def parse_event_data(self, event_data: str) -> CoinbaseWebhookData:
        """Parse the Coinbase Commerce API event data.
        
        Parameters
        ----------
        event_data : str
            Raw event data from Coinbase Commerce API
            
        Returns
        -------
        CoinbaseWebhookData
            Parsed event data
            
        Raises
        ------
        CoinbaseWebhookError
            If required fields are missing
        """
        try:
            data = json.loads(event_data)
            if not data:
                raise CoinbaseWebhookError("No JSON data in request")
                
            # Coinbase Commerce API specific field mapping
            event = data.get('event', {})
            event_type = event.get('type')
            charge_data = event.get('data', {})
            
            # Required fields check
            required_fields = ['code', 'pricing']
            missing_fields = [field for field in required_fields if field not in charge_data]
            if missing_fields:
                raise CoinbaseWebhookError(f"Missing required fields: {', '.join(missing_fields)}")
                
            # Extract pricing information
            pricing = charge_data.get('pricing', {}).get('local', {})
            
            # Extract payment information if available
            payments = charge_data.get('payments', [])
            latest_payment = payments[-1] if payments else {}
            
            # Map Coinbase Commerce API fields to our webhook data format
            status = self._map_status(event_type, charge_data.get('status', ''))
            if status not in ('webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid'):
                status = 'webhook_recieved'
                
            webhook_data: CoinbaseWebhookData = {
                'transaction_id': charge_data['code'],
                'amount': float(pricing.get('amount', 0.0)),
                'currency': pricing.get('currency', 'USD'),
                'status': cast(Literal['webhook_recieved', 'sent_to_websocket', 'sent_to_processor', 'paid'], status),
                'user_id': charge_data.get('metadata', {}).get('user_id', ''),
                'subscription_id': charge_data.get('metadata', {}).get('subscription_id', ''),
                'charge_code': charge_data.get('code'),
                'payment_method': latest_payment.get('network'),
                'confirmed_at': latest_payment.get('confirmed_at')
            }
            
            # Verify the charge with Coinbase Commerce API
            if webhook_data['charge_code']:
                try:
                    self._verifier.verify_charge(webhook_data['charge_code'])
                except ValueError as e:
                    print(f"Warning: Charge verification failed: {str(e)}")
                    
            return webhook_data
            
        except (ValueError, KeyError) as e:
            raise CoinbaseWebhookError(f"Error parsing event data: {str(e)}")

    def _map_status(self, event_type: str, status: str) -> str:
        """Map Coinbase Commerce API status to our internal status.
        
        Parameters
        ----------
        event_type : str
            The event type from Coinbase Commerce API
        status : str
            The status from Coinbase Commerce API
            
        Returns
        -------
        str
            Our internal status representation
        """
        if event_type == 'charge:created':
            return 'webhook_recieved'
        elif event_type == 'charge:confirmed' and status == 'COMPLETED':
            return 'paid'
        elif event_type == 'charge:failed':
            return 'webhook_recieved'
        elif event_type == 'charge:delayed':
            return 'sent_to_processor'
        elif event_type == 'charge:pending':
            return 'sent_to_websocket'
        elif event_type == 'charge:resolved':
            return 'paid'
        else:
            return 'webhook_recieved'

    def _item_name_provider(self, event_data: CoinbaseWebhookData) -> str:
        """Get the item name from the provider.
        
        Parameters
        ----------
        event_data : CoinbaseWebhookData
            The parsed event data
            
        Returns
        -------
        str
            The item name
        """
        return f"Coinbase Payment ({event_data.get('payment_method', 'crypto')})"

    def _get_one_time_payment_data(self, event_data: CoinbaseWebhookData) -> OneTimePaymentData[ITEM_CATEGORY]:
        """Get one-time payment data from the event data.
        
        Parameters
        ----------
        event_data : CoinbaseWebhookData
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
            time_bought=event_data.get('confirmed_at') or datetime.now().isoformat(),
            status=event_data['status'],
            quantity=1
        )

    def _get_subscription_payment_data(self, event_data: CoinbaseWebhookData) -> SubscriptionPaymentData[ITEM_CATEGORY]:
        """Get subscription payment data from the event data.
        
        Parameters
        ----------
        event_data : CoinbaseWebhookData
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
            time_bought=event_data.get('confirmed_at') or datetime.now().isoformat(),
            status=event_data['status']
        ) 