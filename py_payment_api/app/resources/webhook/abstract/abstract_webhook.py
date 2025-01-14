from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, final
from flask import request
from ....verifiers import SignatureVerifier
from ....services.forwarder.abstract.forwarder import Forwarder
from ....services.store.payment.abstract.item_collection_service import ItemCollectionService
from ....services.store.payment.abstract.payment_handler import PaymentHandler
from ....services.store.payment.abstract.item_collection_service import ItemCollectionService
from ....enums import PaymentProvider

class AbstractWebhook(ABC):
    """
    Abstract class for webhook handling.
    """
    __verifier: SignatureVerifier
    __provider_type : PaymentProvider
    __get_signature_function: Callable[[], str]
    def __init__(self, 
                verifier : SignatureVerifier,
                forwarder: Forwarder,
            ) -> None:
        """
        Initialize the webhook with a verification function.

        Parameters
        ----------
        verify_function : callable
            A function to verify the signature of the webhook event.
        """
        self.__verifier = verifier
        self.__forwarder = forwarder
    @final
    def post(self):
        """
        Handle the POST request for the webhook.
        """
        data = request.get_data(as_text=True)
        self.__verifier.verify_header_signature(data, data.header)
   
        event_data = self.parse_event_data(data)

    @abstractmethod
    def process_event(self, event_data: dict, is_one_time_payment: bool):
        """
        Process the event data received from the webhook.
        """
        pass

    @abstractmethod
    def parse_event_data(self, event_data: dict) -> Dict[str, Any]:
        """
        Parse the event data into a structured format.
        """
        pass

    @abstractmethod
    def is_one_time_payment(self) -> bool:
        """
        Determine if the event is a one-time payment.

        Returns
        -------
        bool
            True if it is a one-time payment, False otherwise.
        """
        pass 