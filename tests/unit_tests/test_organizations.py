import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.organizations import Organization, OrganizationPredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def org_instance(mock_connection):
    return Organization(
        connection_object=mock_connection,
        id=20,
        name="Acme Corp",
        disabled=False,
        business_unit=True,
        manager=Person(connection_object=mock_connection, id=5, name="Manager"),
    )


def test_organization_initialization(org_instance):
    assert isinstance(org_instance, Organization)
    assert org_instance.__resourceUrl__ == "organizations"
    assert org_instance.id == 20
    assert org_instance.name == "Acme Corp"
    assert org_instance.business_unit is True
    assert isinstance(org_instance.manager, Person)
    assert org_instance.manager.name == "Manager"


def test_organization_from_data(mock_connection):
    data = {
        "id": 20,
        "name": "Acme Corp",
        "disabled": False,
        "manager": {"id": 5, "name": "Manager"},
        "substitute": {"id": 6, "name": "Sub"},
        "parent": {"id": 10, "name": "Parent Corp"},
    }
    org = Organization.from_data(mock_connection, data)
    assert isinstance(org, Organization)
    assert org.id == 20
    assert isinstance(org.manager, Person)
    assert isinstance(org.substitute, Person)
    assert isinstance(org.parent, Organization)
    assert org.parent.name == "Parent Corp"


def test_get_organization_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 20, "name": "Acme Corp"}
    result = Organization.get_by_id(mock_connection, 20)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/20", "GET"
    )
    assert isinstance(result, Organization)
    assert result.id == 20


def test_get_organizations(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Org A"},
        {"id": 2, "name": "Org B"},
    ]
    results = Organization.get_organizations(mock_connection)
    assert len(results) == 2
    assert all(isinstance(r, Organization) for r in results)


def test_get_organizations_with_predefined_filter(mock_connection):
    mock_connection.api_call.return_value = []
    Organization.get_organizations(mock_connection, predefinedFilter=OrganizationPredefinedFilter.internal)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/internal", "GET"
    )


def test_create_organization(mock_connection):
    mock_connection.api_call.return_value = {"id": 21, "name": "New Org"}
    result = Organization.create(mock_connection, {"name": "New Org"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations", "POST", {"name": "New Org"}
    )
    assert isinstance(result, Organization)
    assert result.id == 21


def test_update_organization(mock_connection, org_instance):
    mock_connection.api_call.return_value = {"id": 20, "name": "Updated Org"}
    result = org_instance.update({"name": "Updated Org"})
    assert isinstance(result, Organization)
    assert result.name == "Updated Org"


def test_enable_organization(mock_connection, org_instance):
    mock_connection.api_call.return_value = {"id": 20, "name": "Acme Corp", "disabled": False}
    org_instance.enable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/20", "PATCH", {"disabled": False}
    )


def test_disable_organization(mock_connection, org_instance):
    mock_connection.api_call.return_value = {"id": 20, "name": "[OLD] Acme Corp", "disabled": True}
    org_instance.disable(prefix="[OLD] ")
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/20", "PATCH",
        {"disabled": True, "name": "[OLD] Acme Corp"}
    )


def test_archive_organization(mock_connection, org_instance):
    mock_connection.api_call.return_value = {"id": 20, "name": "Acme Corp"}
    result = org_instance.archive()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/20/archive", "POST"
    )
    assert isinstance(result, Organization)


def test_trash_organization(mock_connection, org_instance):
    mock_connection.api_call.return_value = {"id": 20, "name": "Acme Corp"}
    result = org_instance.trash()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/20/trash", "POST"
    )
    assert isinstance(result, Organization)


def test_restore_organization(mock_connection, org_instance):
    mock_connection.api_call.return_value = {"id": 20, "name": "Acme Corp"}
    result = org_instance.restore()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/20/restore", "POST"
    )
    assert isinstance(result, Organization)


def test_get_people(mock_connection, org_instance):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    results = org_instance.get_people()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/20/people", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(p, Person) for p in results)


def test_get_children(mock_connection, org_instance):
    mock_connection.api_call.return_value = [
        {"id": 30, "name": "Child Org"},
    ]
    results = org_instance.get_children()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/20/child_organizations", "GET"
    )
    assert len(results) == 1
    assert isinstance(results[0], Organization)
