from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, final
from flask import request
class AbstractWebhook(ABC):
    """
    Abstract class for webhook handling.
    """
    __verify_function: Callable[[str], bool]
    __get_signature_function: Callable[[], str]
    def __init__(self, get_signature_function: Callable[[], str],
                  verify_function: Callable[[str], bool],
                  parse_event_data_function: Callable[[str], Dict[str, Any]],
                  is_one_time_payment_function: Callable[[], bool]):
        """
        Initialize the webhook with a verification function.

        Parameters
        ----------
        verify_function : callable
            A function to verify the signature of the webhook event.
        """
        self.__verify_function = verify_function
        self.__get_signature_function = get_signature_function

    @final
    def post(self):
        """
        Handle the POST request for the webhook.
        """
        data = request.get_data(as_text=True)
        signature = self.__get_signature_function(data)

        if not self.__verify_function(data, signature):
            return {'status': 'error', 'message': 'Invalid signature'}, 400
        
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