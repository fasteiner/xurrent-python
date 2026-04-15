import pytest
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.requests import Request
from xurrent.tasks import Task
from xurrent.workflows import Workflow
from xurrent.organizations import Organization
from xurrent.services import Service
from xurrent.calendars import Calendar
from xurrent.holidays import Holiday


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def request_instance(mock_connection):
    return Request(
        connection_object=mock_connection,
        id=1,
        subject="Test request",
        status="assigned",
    )


@pytest.fixture
def task_instance(mock_connection):
    return Task(
        connection_object=mock_connection,
        id=2,
        subject="Test task",
    )


@pytest.fixture
def workflow_instance(mock_connection):
    return Workflow(
        connection_object=mock_connection,
        id=3,
        subject="Test workflow",
    )


@pytest.fixture
def person_instance(mock_connection):
    return Person(
        connection_object=mock_connection,
        id=4,
        name="Alice",
    )


@pytest.fixture
def org_instance(mock_connection):
    return Organization(
        connection_object=mock_connection,
        id=5,
        name="Acme Corp",
    )


@pytest.fixture
def service_instance(mock_connection):
    return Service(
        connection_object=mock_connection,
        id=6,
        name="IT Support",
    )


@pytest.fixture
def calendar_instance(mock_connection):
    return Calendar(
        connection_object=mock_connection,
        id=7,
        name="Business Hours",
    )


@pytest.fixture
def holiday_instance(mock_connection):
    return Holiday(
        connection_object=mock_connection,
        id=8,
        name="Christmas",
        start_at="2026-12-25T00:00:00Z",
        end_at="2026-12-26T00:00:00Z",
    )


@pytest.fixture
def team_instance(mock_connection):
    return Team(
        connection_object=mock_connection,
        id=9,
        name="Ops Team",
    )


# -------------------------
# Request new sub-resources
# -------------------------

def test_request_get_attachments(mock_connection, request_instance):
    mock_connection.api_call.return_value = [{"id": 1, "filename": "doc.pdf"}]
    result = request_instance.get_attachments()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/1/attachments", "GET"
    )
    assert result == [{"id": 1, "filename": "doc.pdf"}]


def test_request_get_knowledge_articles(mock_connection, request_instance):
    from xurrent.knowledge_articles import KnowledgeArticle
    mock_connection.api_call.return_value = [
        {"id": 1, "subject": "KA 1"},
        {"id": 2, "subject": "KA 2"},
    ]
    results = request_instance.get_knowledge_articles()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/1/knowledge_articles", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, KnowledgeArticle) for r in results)


def test_request_get_automation_rules(mock_connection, request_instance):
    mock_connection.api_call.return_value = [{"id": 1, "name": "Rule A"}]
    result = request_instance.get_automation_rules()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/1/automation_rules", "GET"
    )
    assert result == [{"id": 1, "name": "Rule A"}]


def test_request_get_tags(mock_connection, request_instance):
    mock_connection.api_call.return_value = [{"id": 1, "name": "urgent"}]
    result = request_instance.get_tags()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/1/tags", "GET"
    )
    assert result == [{"id": 1, "name": "urgent"}]


def test_request_get_watches(mock_connection, request_instance):
    mock_connection.api_call.return_value = [{"id": 1, "person_id": 42}]
    result = request_instance.get_watches()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/1/watches", "GET"
    )
    assert result == [{"id": 1, "person_id": 42}]


# ----------------------
# Task new sub-resources
# ----------------------

def test_task_get_notes(mock_connection, task_instance):
    notes_data = [{"id": 1, "text": "Note 1"}]
    mock_connection.api_call.return_value = notes_data
    result = task_instance.get_notes()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/tasks/2/notes", "GET"
    )
    assert result == notes_data


def test_task_add_note_string(mock_connection, task_instance):
    mock_connection.api_call.return_value = {"id": 1, "text": "A note"}
    task_instance.add_note("A note")
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/tasks/2/notes", "POST", {"text": "A note"}
    )


def test_task_add_note_dict(mock_connection, task_instance):
    note = {"text": "A note", "internal": True}
    mock_connection.api_call.return_value = {"id": 1, **note}
    task_instance.add_note(note)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/tasks/2/notes", "POST", note
    )


def test_task_get_approvals(mock_connection, task_instance):
    mock_connection.api_call.return_value = [{"id": 1, "status": "pending"}]
    result = task_instance.get_approvals()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/tasks/2/approvals", "GET"
    )
    assert result == [{"id": 1, "status": "pending"}]


def test_task_get_cis(mock_connection, task_instance):
    from xurrent.configuration_items import ConfigurationItem
    mock_connection.api_call.return_value = [
        {"id": 1, "label": "CI-1"},
        {"id": 2, "label": "CI-2"},
    ]
    results = task_instance.get_cis()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/tasks/2/cis", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, ConfigurationItem) for r in results)


def test_task_get_predecessors(mock_connection, task_instance):
    mock_connection.api_call.return_value = [{"id": 1, "subject": "Predecessor"}]
    results = task_instance.get_predecessors()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/tasks/2/predecessors", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Task) for r in results)


def test_task_get_successors(mock_connection, task_instance):
    mock_connection.api_call.return_value = [{"id": 1, "subject": "Successor"}]
    results = task_instance.get_successors()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/tasks/2/successors", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Task) for r in results)


def test_task_get_service_instances(mock_connection, task_instance):
    from xurrent.service_instances import ServiceInstance
    mock_connection.api_call.return_value = [{"id": 1, "name": "SI A"}]
    results = task_instance.get_service_instances()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/tasks/2/service_instances", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, ServiceInstance) for r in results)


# --------------------------
# Workflow new sub-resources
# --------------------------

def test_workflow_get_notes(mock_connection, workflow_instance):
    notes_data = [{"id": 1, "text": "Note 1"}]
    mock_connection.api_call.return_value = notes_data
    result = workflow_instance.get_notes()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/workflows/3/notes", "GET"
    )
    assert result == notes_data


def test_workflow_add_note_string(mock_connection, workflow_instance):
    mock_connection.api_call.return_value = {"id": 1, "text": "A note"}
    workflow_instance.add_note("A note")
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/workflows/3/notes", "POST", {"text": "A note"}
    )


def test_workflow_get_requests(mock_connection, workflow_instance):
    mock_connection.api_call.return_value = [
        {"id": 1, "subject": "Req A"},
        {"id": 2, "subject": "Req B"},
    ]
    results = workflow_instance.get_requests()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/workflows/3/requests", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Request) for r in results)


def test_workflow_get_problems(mock_connection, workflow_instance):
    from xurrent.problems import Problem
    mock_connection.api_call.return_value = [{"id": 1, "subject": "Problem A"}]
    results = workflow_instance.get_problems()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/workflows/3/problems", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Problem) for r in results)


def test_workflow_get_phases(mock_connection, workflow_instance):
    phases_data = [{"id": 1, "name": "Phase 1"}]
    mock_connection.api_call.return_value = phases_data
    result = workflow_instance.get_phases()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/workflows/3/phases", "GET"
    )
    assert result == phases_data


# -------------------------
# Person new sub-resources
# -------------------------

def test_person_get_cis(mock_connection, person_instance):
    from xurrent.configuration_items import ConfigurationItem
    mock_connection.api_call.return_value = [{"id": 1, "label": "CI-1"}]
    results = person_instance.get_cis()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/people/4/cis", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, ConfigurationItem) for r in results)


def test_person_get_addresses(mock_connection, person_instance):
    addr_data = [{"id": 1, "street": "Main St"}]
    mock_connection.api_call.return_value = addr_data
    result = person_instance.get_addresses()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/people/4/addresses", "GET"
    )
    assert result == addr_data


def test_person_get_out_of_office_periods(mock_connection, person_instance):
    from xurrent.out_of_office_periods import OutOfOfficePeriod
    mock_connection.api_call.return_value = [
        {"id": 1, "start_at": "2026-01-01T00:00:00Z", "end_at": "2026-01-07T00:00:00Z"}
    ]
    results = person_instance.get_out_of_office_periods()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/people/4/out_of_office_periods", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, OutOfOfficePeriod) for r in results)


def test_person_get_skill_pools(mock_connection, person_instance):
    from xurrent.skill_pools import SkillPool
    mock_connection.api_call.return_value = [{"id": 1, "name": "Pool A"}]
    results = person_instance.get_skill_pools()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/people/4/skill_pools", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, SkillPool) for r in results)


# ------------------------------
# Organization new sub-resources
# ------------------------------

def test_org_get_addresses(mock_connection, org_instance):
    addr_data = [{"id": 1, "street": "HQ Street"}]
    mock_connection.api_call.return_value = addr_data
    result = org_instance.get_addresses()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/5/addresses", "GET"
    )
    assert result == addr_data


def test_org_get_contracts(mock_connection, org_instance):
    from xurrent.contracts import Contract
    mock_connection.api_call.return_value = [{"id": 1, "name": "Support"}]
    results = org_instance.get_contracts()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/5/contracts", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Contract) for r in results)


def test_org_get_risks(mock_connection, org_instance):
    from xurrent.risks import Risk
    mock_connection.api_call.return_value = [{"id": 1, "subject": "Risk A"}]
    results = org_instance.get_risks()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/5/risks", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Risk) for r in results)


def test_org_get_time_allocations(mock_connection, org_instance):
    from xurrent.time_allocations import TimeAllocation
    mock_connection.api_call.return_value = [{"id": 1, "name": "TA A"}]
    results = org_instance.get_time_allocations()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/organizations/5/time_allocations", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, TimeAllocation) for r in results)


# -------------------------
# Service new sub-resources
# -------------------------

def test_service_get_workflows(mock_connection, service_instance):
    mock_connection.api_call.return_value = [{"id": 1, "subject": "Wf A"}]
    results = service_instance.get_workflows()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/services/6/workflows", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Workflow) for r in results)


def test_service_get_service_instances(mock_connection, service_instance):
    from xurrent.service_instances import ServiceInstance
    mock_connection.api_call.return_value = [{"id": 1, "name": "SI A"}]
    results = service_instance.get_service_instances()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/services/6/service_instances", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, ServiceInstance) for r in results)


def test_service_get_risks(mock_connection, service_instance):
    from xurrent.risks import Risk
    mock_connection.api_call.return_value = [{"id": 1, "subject": "Risk A"}]
    results = service_instance.get_risks()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/services/6/risks", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Risk) for r in results)


def test_service_get_service_offerings(mock_connection, service_instance):
    from xurrent.service_offerings import ServiceOffering
    mock_connection.api_call.return_value = [{"id": 1, "name": "Gold"}]
    results = service_instance.get_service_offerings()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/services/6/service_offerings", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, ServiceOffering) for r in results)


# --------------------------
# Calendar new sub-resources
# --------------------------

def test_calendar_get_duration(mock_connection, calendar_instance):
    mock_connection.api_call.return_value = {"duration": 3600}
    result = calendar_instance.get_duration(
        start="2026-01-01T09:00:00Z", end="2026-01-01T10:00:00Z"
    )
    call_args = mock_connection.api_call.call_args
    assert "/calendars/7/duration" in call_args[0][0]
    assert "start=2026-01-01T09:00:00Z" in call_args[0][0]
    assert "end=2026-01-01T10:00:00Z" in call_args[0][0]
    assert call_args[0][1] == "GET"
    assert result == {"duration": 3600}


def test_calendar_get_hours(mock_connection, calendar_instance):
    hours_data = [{"id": 1, "day": "monday", "time_from": "08:00", "time_until": "17:00"}]
    mock_connection.api_call.return_value = hours_data
    result = calendar_instance.get_hours()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/calendars/7/hours", "GET"
    )
    assert result == hours_data


def test_calendar_get_holidays(mock_connection, calendar_instance):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Christmas", "start_at": "2026-12-25T00:00:00Z", "end_at": "2026-12-26T00:00:00Z"}
    ]
    results = calendar_instance.get_holidays()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/calendars/7/holidays", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Holiday) for r in results)


# ----------------------
# Team new sub-resources
# ----------------------

def test_team_get_service_instances(mock_connection, team_instance):
    from xurrent.service_instances import ServiceInstance
    mock_connection.api_call.return_value = [{"id": 1, "name": "SI A"}]
    results = team_instance.get_service_instances()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/teams/9/service_instances", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, ServiceInstance) for r in results)


# -------------------------
# Holiday new sub-resources
# -------------------------

def test_holiday_get_calendars(mock_connection, holiday_instance):
    mock_connection.api_call.return_value = [{"id": 1, "name": "Business Hours"}]
    results = holiday_instance.get_calendars()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/holidays/8/calendars", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Calendar) for r in results)


# -------------------------
# Core utility methods
# -------------------------

def test_search(mock_connection):
    mock_connection.api_call.return_value = [{"id": 1, "type": "request"}]
    mock_connection.search = lambda query, types=None: mock_connection.api_call(
        f"/search?q={query}", "GET"
    )
    result = mock_connection.search("password reset")
    mock_connection.api_call.assert_called_once_with("/search?q=password reset", "GET")
    assert result == [{"id": 1, "type": "request"}]


def test_search_core():
    helper = XurrentApiHelper(
        "https://api.example.com", api_key="key", api_account="acct", resolve_user=False
    )
    helper.api_call = MagicMock(return_value=[{"id": 1}])
    result = helper.search("test query")
    helper.api_call.assert_called_once_with("/search?q=test query", "GET")
    assert result == [{"id": 1}]


def test_search_with_types_core():
    helper = XurrentApiHelper(
        "https://api.example.com", api_key="key", api_account="acct", resolve_user=False
    )
    helper.api_call = MagicMock(return_value=[])
    helper.search("test query", types=["request", "person"])
    helper.api_call.assert_called_once_with("/search?q=test query&types=request,person", "GET")


def test_bulk_import_core():
    helper = XurrentApiHelper(
        "https://api.example.com", api_key="key", api_account="acct", resolve_user=False
    )
    helper.api_call = MagicMock(return_value={"status": "done"})
    result = helper.bulk_import("name,email\nAlice,a@b.com", "people")
    helper.api_call.assert_called_once_with("/import", method="POST", data={
        "type": "people",
        "import_format": "csv",
        "data": "name,email\nAlice,a@b.com",
    })
    assert result == {"status": "done"}


def test_list_archive_core():
    helper = XurrentApiHelper(
        "https://api.example.com", api_key="key", api_account="acct", resolve_user=False
    )
    helper.api_call = MagicMock(return_value=[])
    helper.list_archive()
    helper.api_call.assert_called_once_with("/archive", "GET")


def test_list_trash_core():
    helper = XurrentApiHelper(
        "https://api.example.com", api_key="key", api_account="acct", resolve_user=False
    )
    helper.api_call = MagicMock(return_value=[])
    helper.list_trash()
    helper.api_call.assert_called_once_with("/trash", "GET")


def test_list_audit_lines_core():
    helper = XurrentApiHelper(
        "https://api.example.com", api_key="key", api_account="acct", resolve_user=False
    )
    helper.api_call = MagicMock(return_value=[])
    helper.list_audit_lines()
    helper.api_call.assert_called_once_with("/audit_lines", "GET")
