import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.sites import Site, SitePredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def site_instance(mock_connection):
    return Site(
        connection_object=mock_connection,
        id=30,
        name="HQ",
        city="Vienna",
        country="AT",
        time_zone="Europe/Vienna",
        disabled=False,
    )


def test_site_initialization(site_instance):
    assert isinstance(site_instance, Site)
    assert site_instance.__resourceUrl__ == "sites"
    assert site_instance.id == 30
    assert site_instance.name == "HQ"
    assert site_instance.city == "Vienna"
    assert site_instance.country == "AT"
    assert site_instance.disabled is False


def test_site_from_data(mock_connection):
    data = {"id": 30, "name": "HQ", "city": "Vienna", "country": "AT", "disabled": False}
    site = Site.from_data(mock_connection, data)
    assert isinstance(site, Site)
    assert site.id == 30
    assert site.city == "Vienna"


def test_get_site_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 30, "name": "HQ"}
    result = Site.get_by_id(mock_connection, 30)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/sites/30", "GET"
    )
    assert isinstance(result, Site)


def test_get_sites(mock_connection):
    mock_connection.api_call.return_value = [{"id": 1, "name": "Site A"}, {"id": 2, "name": "Site B"}]
    results = Site.get_sites(mock_connection)
    assert len(results) == 2
    assert all(isinstance(r, Site) for r in results)


def test_get_sites_with_predefined_filter(mock_connection):
    mock_connection.api_call.return_value = []
    Site.get_sites(mock_connection, predefinedFilter=SitePredefinedFilter.enabled)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/sites/enabled", "GET"
    )


def test_create_site(mock_connection):
    mock_connection.api_call.return_value = {"id": 31, "name": "New Site"}
    result = Site.create(mock_connection, {"name": "New Site"})
    assert isinstance(result, Site)
    assert result.id == 31


def test_update_site(mock_connection, site_instance):
    mock_connection.api_call.return_value = {"id": 30, "name": "HQ Updated"}
    result = site_instance.update({"name": "HQ Updated"})
    assert isinstance(result, Site)


def test_enable_site(mock_connection, site_instance):
    mock_connection.api_call.return_value = {"id": 30, "name": "HQ", "disabled": False}
    site_instance.enable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/sites/30", "PATCH", {"disabled": False}
    )


def test_disable_site(mock_connection, site_instance):
    mock_connection.api_call.return_value = {"id": 30, "name": "[OLD] HQ", "disabled": True}
    site_instance.disable(prefix="[OLD] ")
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/sites/30", "PATCH", {"disabled": True, "name": "[OLD] HQ"}
    )


def test_archive_site(mock_connection, site_instance):
    mock_connection.api_call.return_value = {"id": 30, "name": "HQ"}
    result = site_instance.archive()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/sites/30/archive", "POST"
    )
    assert isinstance(result, Site)


def test_trash_site(mock_connection, site_instance):
    mock_connection.api_call.return_value = {"id": 30, "name": "HQ"}
    result = site_instance.trash()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/sites/30/trash", "POST"
    )
    assert isinstance(result, Site)


def test_restore_site(mock_connection, site_instance):
    mock_connection.api_call.return_value = {"id": 30, "name": "HQ"}
    result = site_instance.restore()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/sites/30/restore", "POST"
    )
    assert isinstance(result, Site)
