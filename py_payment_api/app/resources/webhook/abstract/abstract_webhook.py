from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, final, Optional, cast
from flask import request, Response
from flask_restful import Resource # type: ignore
from ....verifiers import SignatureVerifier
from ....services.forwarder.abstract.forwarder import Forwarder
from ....services.store.payment.abstract.item_collection_service import ItemCollectionService
from ....services.store.payment.abstract.payment_handler import PaymentHandler
from ....services.store.payment.one_time.one_time_payment_data import OneTimePaymentData
from ....services.store.payment.subscription.subscription_payment_data import SubscriptionPaymentData
from ....services import PaymentProvider, ItemType
from typing import TypeVar, Generic, TypedDict
from enum import StrEnum
from flask_restful import reqparse
from ....services import get_services, Services, ItemType
PROVIDER_DATA = TypeVar('PROVIDER_DATA')

ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)

class AbstractWebhook(ABC, Resource, Generic[PROVIDER_DATA, ITEM_CATEGORY]):
    """
    Abstract class for webhook handling.
    """
    __verifier: SignatureVerifier
    __provider_type: PaymentProvider
    __forwarder: Forwarder | None
    __services: Services[Any, Any]
    def __init__(self, 
                 provider_type: PaymentProvider,
                verifier: SignatureVerifier,
                forwarder: Forwarder | None = None) -> None:
        """
        Initialize the webhook with a verification function.

        Parameters
        ----------
        verifier : SignatureVerifier
            A verifier to check the signature of the webhook event.
        forwarder : Forwarder
            A forwarder to handle webhook event forwarding.
        """
        self.__verifier = verifier
        self.__forwarder = forwarder
        self.__provider_type = provider_type
        self.__services = get_services()
    @final
    def post(self) -> Response:
        """
        Handle the POST request for the webhook.
        Returns
        -------
        Response
            The HTTP response object.
        """
        data: str = request.get_data(as_text=True)
        headers: Dict[str, Any] = dict(request.headers)
        self.__verifier.verify_header_signature(headers, headers.get('X-Signature', {}))
   
        provider_data: PROVIDER_DATA = self.parse_event_data(data)
        item_purchase_type: ItemType = self.__get_item_purchase_type(provider_data)
        if self.__forwarder is not None:
            self.__forwarder.forward_event(provider_data.__dict__)
        else:
            match item_purchase_type:
                case ItemType.ONE_TIME_PAYMENT:
                    self.__services._handle_one_time_payment(self.__provider_type, self._get_one_time_payment_data(provider_data))
                case ItemType.SUBSCRIPTION:
                    self.__services._handle_subscription(self.__provider_type, self._get_subscription_payment_data(provider_data))
                case ItemType.UNKNOWN:
                    raise ValueError(f"Unknown item purchase type: {item_purchase_type}")
        return Response(status=200)

    @abstractmethod
    def _get_one_time_payment_data(self, event_data: PROVIDER_DATA) -> OneTimePaymentData[Any]:
        """
        Get the one-time payment data from the event data.
        """
        pass

    @abstractmethod
    def _get_subscription_payment_data(self, event_data: PROVIDER_DATA) -> SubscriptionPaymentData[Any]:
        """
        Get the subscription payment data from the event data.
        """
        pass

    @abstractmethod
    def _item_name_provider(self, event_data: PROVIDER_DATA) -> str:
        """
        Get the item name from the provider.
        """
        pass

    @final
    def __get_item_purchase_type(self, event_data: PROVIDER_DATA) -> ItemType:
        """
        Check if the payment is a one-time payment.
        """
        result = self.__services.get_purchase_type(self._item_name_provider(event_data))
        return result

    @abstractmethod
    def parse_event_data(self, event_data: str) -> PROVIDER_DATA:
        """
        Parse the event data into a structured format.
        
        Parameters
        ----------
        event_data : str
            The raw event data string
            
        Returns
        -------
        PROVIDER_DATA
            The parsed event data
        """
        pass
