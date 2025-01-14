from ExtendablePaymentApi.py_payment_api.app.services.forwarder.abstract.forwarder import Forwarder
import os
import requests
from typing import Optional, List
from ..store.payment.abstract.item_collection_service import ItemCollectionService

class RestfulForwarder(Forwarder):

    def __init__(self, url: str, logger: Optional[List[ItemCollectionService]] = None) -> None:
        super().__init__()
        self.url = url
        self.route = os.getenv('ROUTE', "/creditor_api")
        self.logger = logger
        if self.logger:
            for log_service in self.logger:
                log_service.log(f"Initializing RestfulForwarder with URL: {self.url} and route: {self.route}")

    def forward_event(self, event_data: dict) -> None:
        full_url = f"{self.url}{self.route}"
        if self.logger:
            for log_service in self.logger:
                log_service.log(f"Forwarding event to URL: {full_url} with data: {event_data}")
        try:
            response = requests.post(full_url, json=event_data)
            response.raise_for_status()
            if self.logger:
                for log_service in self.logger:
                    log_service.log(f"Successfully forwarded event to {full_url}")
        except requests.exceptions.RequestException as e:
            if self.logger:
                for log_service in self.logger:
                    log_service.log(f"Failed to forward event to {full_url}: {e}")
            raise