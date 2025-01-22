import pytest
import asyncio
from typing import Dict, Any, cast
from unittest.mock import MagicMock, patch, AsyncMock
from enum import StrEnum
from ..websocket_forwarder import WebSocketForwarder
from ...store.payment.abstract.item_collection_service import ItemCollectionService

class TestItemCategory(StrEnum):
    TEST_ITEM = "test_item"

@pytest.fixture
def websocket_forwarder() -> WebSocketForwarder:
    return WebSocketForwarder()

@pytest.mark.asyncio
@patch('websockets.connect')
async def test_websocket_forwarder_connect(mock_connect: MagicMock, websocket_forwarder: WebSocketForwarder) -> None:
    """Test websocket connection."""
    mock_websocket = AsyncMock()
    mock_connect.return_value.__aenter__ = AsyncMock(return_value=mock_websocket)
    await websocket_forwarder.connect()
    assert mock_connect.called

@pytest.mark.asyncio
@patch('websockets.connect')
async def test_websocket_forwarder_forward_event(mock_connect: MagicMock, websocket_forwarder: WebSocketForwarder) -> None:
    """Test forwarding data through websocket."""
    mock_websocket = AsyncMock()
    mock_connect.return_value.__aenter__ = AsyncMock(return_value=mock_websocket)
    mock_websocket.send = AsyncMock()
    mock_websocket.recv = AsyncMock(return_value="success")

    test_data = {
        "order_id": "test123",
        "status": "paid",
        "message": "test message"
    }
    await websocket_forwarder.connect()
    websocket_forwarder.forward_event(test_data)
