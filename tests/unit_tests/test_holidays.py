import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.holidays import Holiday


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def holiday_instance(mock_connection):
    return Holiday(
        connection_object=mock_connection,
        id=60,
        name="Christmas",
        start_at="2026-12-25T00:00:00Z",
        end_at="2026-12-26T00:00:00Z",
    )


def test_holiday_initialization(holiday_instance):
    assert isinstance(holiday_instance, Holiday)
    assert holiday_instance.__resourceUrl__ == "holidays"
    assert holiday_instance.id == 60
    assert holiday_instance.name == "Christmas"


def test_holiday_from_data(mock_connection):
    data = {"id": 60, "name": "Christmas", "start_at": "2026-12-25T00:00:00Z", "end_at": "2026-12-26T00:00:00Z"}
    holiday = Holiday.from_data(mock_connection, data)
    assert isinstance(holiday, Holiday)
    assert holiday.id == 60
    assert holiday.name == "Christmas"


def test_get_holiday_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 60, "name": "Christmas", "start_at": "2026-12-25T00:00:00Z", "end_at": "2026-12-26T00:00:00Z"}
    result = Holiday.get_by_id(mock_connection, 60)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/holidays/60", "GET"
    )
    assert isinstance(result, Holiday)


def test_get_holidays(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "New Year", "start_at": "2026-01-01T00:00:00Z", "end_at": "2026-01-02T00:00:00Z"},
        {"id": 2, "name": "Christmas", "start_at": "2026-12-25T00:00:00Z", "end_at": "2026-12-26T00:00:00Z"},
    ]
    results = Holiday.get_holidays(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/holidays", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Holiday) for r in results)


def test_get_holidays_with_queryfilter(mock_connection):
    mock_connection.api_call.return_value = []
    mock_connection.create_filter_string.return_value = "name=Christmas"
    Holiday.get_holidays(mock_connection, queryfilter={"name": "Christmas"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/holidays?name=Christmas", "GET"
    )


def test_create_holiday(mock_connection):
    mock_connection.api_call.return_value = {"id": 61, "name": "Easter", "start_at": "2026-04-05T00:00:00Z", "end_at": "2026-04-06T00:00:00Z"}
    result = Holiday.create(mock_connection, {"name": "Easter", "start_at": "2026-04-05T00:00:00Z", "end_at": "2026-04-06T00:00:00Z"})
    assert isinstance(result, Holiday)
    assert result.id == 61


def test_update_holiday(mock_connection, holiday_instance):
    mock_connection.api_call.return_value = {"id": 60, "name": "Christmas Day", "start_at": "2026-12-25T00:00:00Z", "end_at": "2026-12-26T00:00:00Z"}
    result = holiday_instance.update({"name": "Christmas Day"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/holidays/60", "PATCH", {"name": "Christmas Day"}
    )
    assert isinstance(result, Holiday)
