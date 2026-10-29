import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.service_instances import ServiceInstance, ServiceInstancePredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def si_instance(mock_connection):
    return ServiceInstance(
        connection_object=mock_connection,
        id=30,
        name="Production SI",
        status="active",
    )


def test_service_instance_initialization(si_instance):
    assert isinstance(si_instance, ServiceInstance)
    assert si_instance.__resourceUrl__ == "service_instances"
    assert si_instance.id == 30
    assert si_instance.name == "Production SI"


def test_service_instance_from_data(mock_connection):
    data = {
        "id": 30,
        "name": "Production SI",
        "status": "active",
        "service": {"id": 5, "name": "My Service"},
    }
    si = ServiceInstance.from_data(mock_connection, data)
    assert isinstance(si, ServiceInstance)
    assert si.id == 30
    from xurrent.services import Service
    assert isinstance(si.service, Service)
    assert si.service.name == "My Service"


def test_get_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 30, "name": "Production SI"}
    result = ServiceInstance.get_by_id(mock_connection, 30)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_instances/30", "GET"
    )
    assert isinstance(result, ServiceInstance)
    assert result.id == 30


def test_get_service_instances(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "SI A"},
        {"id": 2, "name": "SI B"},
    ]
    results = ServiceInstance.get_service_instances(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_instances", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, ServiceInstance) for r in results)


def test_get_service_instances_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    ServiceInstance.get_service_instances(
        mock_connection, predefinedFilter=ServiceInstancePredefinedFilter.active
    )
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_instances/active", "GET"
    )


def test_create_service_instance(mock_connection):
    mock_connection.api_call.return_value = {"id": 31, "name": "New SI"}
    result = ServiceInstance.create(mock_connection, {"name": "New SI"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_instances", "POST", {"name": "New SI"}
    )
    assert isinstance(result, ServiceInstance)
    assert result.id == 31


def test_update_service_instance(mock_connection, si_instance):
    mock_connection.api_call.return_value = {"id": 30, "name": "Updated SI"}
    result = si_instance.update({"name": "Updated SI"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_instances/30", "PATCH", {"name": "Updated SI"}
    )
    assert isinstance(result, ServiceInstance)
    assert result.name == "Updated SI"


def test_get_cis(mock_connection, si_instance):
    from xurrent.configuration_items import ConfigurationItem
    mock_connection.api_call.return_value = [
        {"id": 1, "label": "CI-1"},
        {"id": 2, "label": "CI-2"},
    ]
    results = si_instance.get_cis()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_instances/30/cis", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, ConfigurationItem) for r in results)


def test_get_users(mock_connection, si_instance):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    results = si_instance.get_users()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/service_instances/30/users", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Person) for r in results)
