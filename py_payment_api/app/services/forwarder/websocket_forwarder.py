import asyncio
import websockets
import os
from ExtendablePaymentApi.py_payment_api.app.services.forwarder.abstract.forwarder import Forwarder
from typing import Optional, List
from ExtendablePaymentApi.py_payment_api.app.services.store.payment.abstract.item_collection_service import ItemCollectionService

class WebSocketForwarder(Forwarder):
    def __init__(self, 
                 item_collection_service: ItemCollectionService, 
                 logger: Optional[List[ItemCollectionService]] = None):
        super().__init__(item_collection_service.collect_items)
        self.item_collection_service = item_collection_service
        self.logger = logger
        self.url = os.getenv('WEBSOCKET_URL')
        if not self.url:
            if self.logger:
                for log_service in self.logger:
                    log_service.log("WebSocket URL not set in environment variables.")
            raise ValueError("WebSocket URL not set in environment variables.")
        self.websocket = None
        if self.logger:
            for log_service in self.logger:
                log_service.log(f"Initializing WebSocketForwarder with URL: {self.url}")
        asyncio.run(self.connect())

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.url)
            if self.logger:
                for log_service in self.logger:
                    log_service.log(f"Connected to WebSocket at {self.url}")
        except Exception as e:
            if self.logger:
                for log_service in self.logger:
                    log_service.log(f"Failed to connect to WebSocket: {e}")
            raise

    async def forward_request(self, message: str):
        if self.websocket is None:
            if self.logger:
                for log_service in self.logger:
                    log_service.log("WebSocket not connected. Attempting to reconnect.")
            await self.connect()
        try:
            await self.websocket.send(message)
            if self.logger:
                for log_service in self.logger:
                    log_service.log(f"Sent message: {message}")
            response = await self.websocket.recv()
            if self.logger:
                for log_service in self.logger:
                    log_service.log(f"Received response: {response}")
            return response
        except Exception as e:
            if self.logger:
                for log_service in self.logger:
                    log_service.log(f"Error during forward_request: {e}")
            raise

    async def close(self):
        if self.websocket is not None:
            await self.websocket.close()
            if self.logger:
                for log_service in self.logger:
                    log_service.log("WebSocket connection closed.")

    def _on_forward_event(self, event_data: dict) -> None:
        message = event_data.get('message', '')
        if self.logger:
            for log_service in self.logger:
                log_service.log(f"Forwarding event with message: {message}")
        self.item_collection_service.collect_items(message)
        asyncio.run(self.forward_request(message))
