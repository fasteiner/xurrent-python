import pytest
import os
import sys
from unittest.mock import MagicMock
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.out_of_office_periods import OutOfOfficePeriod, OutOfOfficePeriodPredefinedFilter
from xurrent.time_allocations import TimeAllocation
from xurrent.effort_classes import EffortClass


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def oof_instance(mock_connection):
    return OutOfOfficePeriod(
        connection_object=mock_connection,
        id=50,
        start_at=datetime(2026, 4, 14, 9, 0),
        end_at=datetime(2026, 4, 18, 17, 0),
        reason="Vacation",
        person=Person(connection_object=mock_connection, id=10, name="Alice"),
    )


def test_oof_initialization(oof_instance):
    assert isinstance(oof_instance, OutOfOfficePeriod)
    assert oof_instance.__resourceUrl__ == "out_of_office_periods"
    assert oof_instance.id == 50
    assert oof_instance.reason == "Vacation"
    assert isinstance(oof_instance.person, Person)
    assert oof_instance.person.name == "Alice"


def test_oof_from_data(mock_connection):
    data = {
        "id": 50,
        "start_at": "2026-04-14T09:00:00Z",
        "end_at": "2026-04-18T17:00:00Z",
        "reason": "Vacation",
        "person": {"id": 10, "name": "Alice"},
        "approval_delegate": {"id": 11, "name": "Bob"},
        "effort_class": {"id": 3, "name": "Regular"},
    }
    oof = OutOfOfficePeriod.from_data(mock_connection, data)
    assert isinstance(oof, OutOfOfficePeriod)
    assert isinstance(oof.person, Person)
    assert isinstance(oof.approval_delegate, Person)
    assert isinstance(oof.effort_class, EffortClass)


def test_get_oof_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 50, "start_at": "2026-04-14T09:00:00Z", "end_at": "2026-04-18T17:00:00Z"}
    result = OutOfOfficePeriod.get_by_id(mock_connection, 50)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/out_of_office_periods/50", "GET"
    )
    assert isinstance(result, OutOfOfficePeriod)


def test_get_oof_periods(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "start_at": "2026-04-01T00:00:00Z", "end_at": "2026-04-05T00:00:00Z"},
        {"id": 2, "start_at": "2026-05-01T00:00:00Z", "end_at": "2026-05-03T00:00:00Z"},
    ]
    results = OutOfOfficePeriod.get_out_of_office_periods(mock_connection)
    assert len(results) == 2
    assert all(isinstance(r, OutOfOfficePeriod) for r in results)


def test_get_oof_periods_with_predefined_filter(mock_connection):
    mock_connection.api_call.return_value = []
    OutOfOfficePeriod.get_out_of_office_periods(
        mock_connection, predefinedFilter=OutOfOfficePeriodPredefinedFilter.open
    )
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/out_of_office_periods/open", "GET"
    )


def test_create_oof(mock_connection):
    mock_connection.api_call.return_value = {
        "id": 51,
        "start_at": "2026-06-01T09:00:00Z",
        "end_at": "2026-06-05T17:00:00Z",
    }
    result = OutOfOfficePeriod.create(mock_connection, {"person_id": 10, "start_at": "2026-06-01T09:00:00Z", "end_at": "2026-06-05T17:00:00Z"})
    assert isinstance(result, OutOfOfficePeriod)
    assert result.id == 51


def test_update_oof(mock_connection, oof_instance):
    mock_connection.api_call.return_value = {"id": 50, "start_at": "2026-04-14T09:00:00Z", "end_at": "2026-04-19T17:00:00Z", "reason": "Extended"}
    result = oof_instance.update({"end_at": "2026-04-19T17:00:00Z"})
    assert isinstance(result, OutOfOfficePeriod)


def test_delete_oof(mock_connection, oof_instance):
    mock_connection.api_call.return_value = None
    oof_instance.delete()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/out_of_office_periods/50", "DELETE"
    )
