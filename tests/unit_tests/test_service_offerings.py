import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.service_offerings import ServiceOffering, ServiceOfferingPredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def so_instance(mock_connection):
    return ServiceOffering(
        connection_object=mock_connection,
        id=100,
        name="Gold Support",
        status="available",
    )


def test_service_offering_initialization(so_instance):
    assert isinstance(so_instance, ServiceOffering)
    assert so_instance.__resourceUrl__ == "service_offerings"
    assert so_instance.id == 100
    assert so_instance.name == "Gold Support"


def test_service_offering_from_data(mock_connection):
    data = {
        "id": 100,
        "name": "Gold Support",
        "status": "available",
        "service": {"id": 5, "name": "IT Support"},
    }
    so = ServiceOffering.from_data(mock_connection, data)
    assert isinstance(so, ServiceOffering)
    assert so.id == 100
    from xurrent.services import Service
    assert isinstance(so.service, Service)


def test_get_service_offering_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 100, "name": "Gold Support"}
    result = ServiceOffering.get_by_id(mock_connection, 100)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_offerings/100", "GET"
    )
    assert isinstance(result, ServiceOffering)
    assert result.id == 100


def test_get_service_offerings(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Gold"},
        {"id": 2, "name": "Silver"},
    ]
    results = ServiceOffering.get_service_offerings(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_offerings", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, ServiceOffering) for r in results)


def test_get_service_offerings_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    ServiceOffering.get_service_offerings(
        mock_connection, predefinedFilter=ServiceOfferingPredefinedFilter.catalog
    )
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_offerings/catalog", "GET"
    )


def test_create_service_offering(mock_connection):
    mock_connection.api_call.return_value = {"id": 101, "name": "Platinum"}
    result = ServiceOffering.create(mock_connection, {"name": "Platinum"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_offerings", "POST", {"name": "Platinum"}
    )
    assert isinstance(result, ServiceOffering)
    assert result.id == 101


def test_update_service_offering(mock_connection, so_instance):
    mock_connection.api_call.return_value = {"id": 100, "name": "Updated Gold"}
    result = so_instance.update({"name": "Updated Gold"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_offerings/100", "PATCH", {"name": "Updated Gold"}
    )
    assert isinstance(result, ServiceOffering)
    assert result.name == "Updated Gold"
