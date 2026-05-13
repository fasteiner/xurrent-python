import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.contracts import Contract, ContractPredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def contract_instance(mock_connection):
    return Contract(
        connection_object=mock_connection,
        id=70,
        name="Support Contract",
        status="active",
    )


def test_contract_initialization(contract_instance):
    assert isinstance(contract_instance, Contract)
    assert contract_instance.__resourceUrl__ == "contracts"
    assert contract_instance.id == 70
    assert contract_instance.name == "Support Contract"


def test_contract_from_data(mock_connection):
    data = {
        "id": 70,
        "name": "Support Contract",
        "status": "active",
        "customer": {"id": 10, "name": "Acme Corp"},
    }
    contract = Contract.from_data(mock_connection, data)
    assert isinstance(contract, Contract)
    assert contract.id == 70
    from xurrent.organizations import Organization
    assert isinstance(contract.customer, Organization)
    assert contract.customer.name == "Acme Corp"


def test_get_contract_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 70, "name": "Support Contract"}
    result = Contract.get_by_id(mock_connection, 70)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/contracts/70", "GET"
    )
    assert isinstance(result, Contract)
    assert result.id == 70


def test_get_contracts(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Contract A"},
        {"id": 2, "name": "Contract B"},
    ]
    results = Contract.get_contracts(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/contracts", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Contract) for r in results)


def test_get_contracts_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    Contract.get_contracts(mock_connection, predefinedFilter=ContractPredefinedFilter.active)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/contracts/active", "GET"
    )


def test_create_contract(mock_connection):
    mock_connection.api_call.return_value = {"id": 71, "name": "New Contract"}
    result = Contract.create(mock_connection, {"name": "New Contract"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/contracts", "POST", {"name": "New Contract"}
    )
    assert isinstance(result, Contract)
    assert result.id == 71


def test_update_contract(mock_connection, contract_instance):
    mock_connection.api_call.return_value = {"id": 70, "name": "Updated Contract"}
    result = contract_instance.update({"name": "Updated Contract"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/contracts/70", "PATCH", {"name": "Updated Contract"}
    )
    assert isinstance(result, Contract)
    assert result.name == "Updated Contract"


def test_get_cis(mock_connection, contract_instance):
    from xurrent.configuration_items import ConfigurationItem
    mock_connection.api_call.return_value = [
        {"id": 1, "label": "CI-1"},
        {"id": 2, "label": "CI-2"},
    ]
    results = contract_instance.get_cis()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/contracts/70/cis", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, ConfigurationItem) for r in results)
