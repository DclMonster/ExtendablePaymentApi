from typing import Dict, Any, Generic, TypeVar, Optional, final
from enum import StrEnum
import asyncio
import websockets
from .abstract.single_forwarder import SingleForwarder
from ...services import PurchaseStatus
from websockets.client import WebSocketClientProtocol

@final
class WebSocketForwarder(SingleForwarder):
    """Forwarder that sends data via WebSocket."""
    
    def __init__(self, url: str = "ws://localhost:8765") -> None:
        """Initialize the forwarder.
        
        Parameters
        ----------
        service : ItemCollectionService
            The service to use for status updates
        url : str, optional
            The WebSocket URL to connect to, by default "ws://localhost:8765"
        """
        super().__init__(PurchaseStatus.SENT_TO_WEBSOCKET)
        self._url = url
        self._websocket : Optional[WebSocketClientProtocol] = None

    async def connect(self) -> None:
        """Connect to the WebSocket server."""
        self._websocket = await websockets.connect(self._url)

    @final
    def _on_forward_event(self, data: Dict[str, Any]) -> None:
        """Forward event data via WebSocket.
        
        Parameters
        ----------
        data : Dict[str, Any]
            The data to forward
        """
        # Create event loop if it doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Connect if not connected
        if not self._websocket:
            loop.run_until_complete(self.connect())
        
        # Send data
        if self._websocket:
            loop.run_until_complete(self._websocket.send(str(data)))
