from typing import Dict, List, Any, Tuple
import pytest
from unittest.mock import patch, MagicMock
from ..get_user_orders import GetUserOrders

@pytest.fixture
def resource() -> GetUserOrders:
    return GetUserOrders()

@patch('app.resources.store.get_user_orders.get_services')
def test_get_user_orders_success(mock_get_services: MagicMock, resource: GetUserOrders) -> None:
    # Arrange
    test_user_id = "test_user_123"
    mock_orders: List[Dict[str, str]] = [
        {"order_id": "order1", "status": "completed"},
        {"order_id": "order2", "status": "pending"}
    ]
    mock_service = MagicMock()
    mock_service.get_orders_by_user_id.return_value = mock_orders
    mock_get_services.return_value = mock_service

    # Act
    response, status_code = resource.get()

    # Assert
    assert status_code == 200
    assert response['orders'] == mock_orders
    mock_service.get_orders_by_user_id.assert_called_once_with(test_user_id)

@patch('app.resources.store.get_user_orders.get_services')
def test_get_user_orders_no_orders(mock_get_services: MagicMock, resource: GetUserOrders) -> None:
    # Arrange
    test_user_id = "test_user_123"
    mock_service = MagicMock()
    mock_service.get_orders_by_user_id.return_value = []
    mock_get_services.return_value = mock_service

    # Act
    response, status_code = resource.get()

    # Assert
    assert status_code == 200
    assert response['orders'] == []
    mock_service.get_orders_by_user_id.assert_called_once_with(test_user_id)

