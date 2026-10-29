import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.risks import Risk, RiskPredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def risk_instance(mock_connection):
    return Risk(
        connection_object=mock_connection,
        id=90,
        subject="Data breach risk",
        status="security",
        severity="high",
        manager=Person(connection_object=mock_connection, id=5, name="Manager"),
    )


def test_risk_initialization(risk_instance):
    assert isinstance(risk_instance, Risk)
    assert risk_instance.__resourceUrl__ == "risks"
    assert risk_instance.id == 90
    assert risk_instance.subject == "Data breach risk"
    assert isinstance(risk_instance.manager, Person)


def test_risk_from_data(mock_connection):
    data = {
        "id": 90,
        "subject": "Data breach risk",
        "severity": "high",
        "manager": {"id": 5, "name": "Manager"},
    }
    risk = Risk.from_data(mock_connection, data)
    assert isinstance(risk, Risk)
    assert risk.id == 90
    assert isinstance(risk.manager, Person)


def test_get_risk_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 90, "subject": "Data breach risk"}
    result = Risk.get_by_id(mock_connection, 90)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/risks/90", "GET"
    )
    assert isinstance(result, Risk)
    assert result.id == 90


def test_get_risks(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "subject": "Risk A"},
        {"id": 2, "subject": "Risk B"},
    ]
    results = Risk.get_risks(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/risks", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Risk) for r in results)


def test_get_risks_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    Risk.get_risks(mock_connection, predefinedFilter=RiskPredefinedFilter.open)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/risks/open", "GET"
    )


def test_create_risk(mock_connection):
    mock_connection.api_call.return_value = {"id": 91, "subject": "New Risk"}
    result = Risk.create(mock_connection, {"subject": "New Risk"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/risks", "POST", {"subject": "New Risk"}
    )
    assert isinstance(result, Risk)
    assert result.id == 91


def test_update_risk(mock_connection, risk_instance):
    mock_connection.api_call.return_value = {"id": 90, "subject": "Updated Risk"}
    result = risk_instance.update({"subject": "Updated Risk"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/risks/90", "PATCH", {"subject": "Updated Risk"}
    )
    assert isinstance(result, Risk)
    assert result.subject == "Updated Risk"


def test_archive_risk(mock_connection, risk_instance):
    mock_connection.api_call.return_value = {"id": 90, "subject": "Data breach risk"}
    result = risk_instance.archive()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/risks/90/archive", "POST"
    )
    assert isinstance(result, Risk)


def test_trash_risk(mock_connection, risk_instance):
    mock_connection.api_call.return_value = {"id": 90, "subject": "Data breach risk"}
    result = risk_instance.trash()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/risks/90/trash", "POST"
    )
    assert isinstance(result, Risk)


def test_restore_risk(mock_connection, risk_instance):
    mock_connection.api_call.return_value = {"id": 90, "subject": "Data breach risk"}
    result = risk_instance.restore()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/risks/90/restore", "POST"
    )
    assert isinstance(result, Risk)


def test_get_organizations(mock_connection, risk_instance):
    from xurrent.organizations import Organization
    mock_connection.api_call.return_value = [{"id": 1, "name": "Org A"}]
    results = risk_instance.get_organizations()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/risks/90/organizations", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Organization) for r in results)


def test_get_projects(mock_connection, risk_instance):
    from xurrent.projects import Project
    mock_connection.api_call.return_value = [{"id": 1, "subject": "Proj A"}]
    results = risk_instance.get_projects()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/risks/90/projects", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Project) for r in results)


def test_get_services(mock_connection, risk_instance):
    from xurrent.services import Service
    mock_connection.api_call.return_value = [{"id": 1, "name": "Service A"}]
    results = risk_instance.get_services()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/risks/90/services", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Service) for r in results)
