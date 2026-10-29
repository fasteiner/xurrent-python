import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.closure_codes import ClosureCode


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def cc_instance(mock_connection):
    return ClosureCode(
        connection_object=mock_connection,
        id=120,
        name="Resolved",
    )


def test_closure_code_initialization(cc_instance):
    assert isinstance(cc_instance, ClosureCode)
    assert cc_instance.__resourceUrl__ == "closure_codes"
    assert cc_instance.id == 120
    assert cc_instance.name == "Resolved"


def test_closure_code_from_data(mock_connection):
    data = {"id": 120, "name": "Resolved"}
    cc = ClosureCode.from_data(mock_connection, data)
    assert isinstance(cc, ClosureCode)
    assert cc.id == 120
    assert cc.name == "Resolved"


def test_get_closure_code_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 120, "name": "Resolved"}
    result = ClosureCode.get_by_id(mock_connection, 120)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/closure_codes/120", "GET"
    )
    assert isinstance(result, ClosureCode)
    assert result.id == 120


def test_get_closure_codes(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Resolved"},
        {"id": 2, "name": "Cancelled"},
    ]
    results = ClosureCode.get_closure_codes(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/closure_codes", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, ClosureCode) for r in results)


def test_create_closure_code(mock_connection):
    mock_connection.api_call.return_value = {"id": 121, "name": "Duplicate"}
    result = ClosureCode.create(mock_connection, {"name": "Duplicate"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/closure_codes", "POST", {"name": "Duplicate"}
    )
    assert isinstance(result, ClosureCode)
    assert result.id == 121


def test_update_closure_code(mock_connection, cc_instance):
    mock_connection.api_call.return_value = {"id": 120, "name": "Fixed"}
    result = cc_instance.update({"name": "Fixed"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/closure_codes/120", "PATCH", {"name": "Fixed"}
    )
    assert isinstance(result, ClosureCode)
    assert result.name == "Fixed"
