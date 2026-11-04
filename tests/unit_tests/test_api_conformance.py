"""Regression tests for mismatches with the real API found by tests/smoke/read_only_check.py."""
import os
import sys
from unittest.mock import MagicMock

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper  # noqa: E402
from xurrent.contracts import Contract, ContractStatus  # noqa: E402
from xurrent.problems import Problem, ProblemStatus  # noqa: E402
from xurrent.projects import Project, ProjectCategory, ProjectStatus  # noqa: E402
from xurrent.releases import Release, ReleaseImpact, ReleaseStatus  # noqa: E402
from xurrent.request_templates import RequestTemplate, RequestTemplateCategory  # noqa: E402
from xurrent.risks import Risk, RiskStatus  # noqa: E402
from xurrent.service_instances import ServiceInstance, ServiceInstanceStatus  # noqa: E402
from xurrent.service_offerings import ServiceOffering, ServiceOfferingStatus  # noqa: E402
from xurrent.tasks import Task  # noqa: E402
from xurrent.workflows import Workflow  # noqa: E402

BASE = "https://api.example.com/v1"


@pytest.fixture
def connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = BASE
    return mock


# ---------------------------------------------------------------- Task workflow reference

def test_get_workflow_expand_uses_the_id_of_the_dict_reference(connection):
    # The API returns the workflow of a task as a dict; .id raised AttributeError
    connection.api_call.return_value = {"id": 42, "subject": "Change"}
    task = Task(connection, id=7, workflow={"id": 42, "subject": "Change"})
    workflow = task.get_workflow(expand=True)
    connection.api_call.assert_called_once_with(f"{BASE}/workflows/42", "GET")
    assert isinstance(workflow, Workflow) and workflow.id == 42


def test_get_workflow_without_expand_needs_no_request(connection):
    task = Task(connection, id=7, workflow={"id": 42, "subject": "Change"})
    workflow = task.get_workflow()
    connection.api_call.assert_not_called()
    assert isinstance(workflow, Workflow) and workflow.id == 42


def test_get_workflow_keeps_a_workflow_instance(connection):
    reference = Workflow(connection, id=42, subject="Change")
    assert Task(connection, id=7, workflow=reference).get_workflow() is reference


def test_get_workflow_of_task_expand(connection):
    connection.api_call.side_effect = [
        {"id": 7, "subject": "Task", "workflow": {"id": 42}},
        {"id": 42, "subject": "Change"},
    ]
    workflow = Task.get_workflow_of_task(connection, 7, expand=True)
    assert [c.args for c in connection.api_call.call_args_list] == [
        (f"{BASE}/tasks/7", "GET"), (f"{BASE}/workflows/42", "GET")]
    assert workflow.id == 42 and workflow.subject == "Change"


def test_get_workflow_without_reference_reads_the_task(connection):
    connection.api_call.return_value = {"id": 7, "workflow": {"id": 42, "subject": "Change"}}
    workflow = Task(connection, id=7).get_workflow()
    connection.api_call.assert_called_once_with(f"{BASE}/tasks/7", "GET")
    assert workflow.id == 42


# ---------------------------------------------------------------- enum values of the API

@pytest.mark.parametrize("cls, field, value, member", [
    (Contract, "status", "being_prepared", ContractStatus.being_prepared),
    (Contract, "status", "scheduled_for_activation", ContractStatus.scheduled_for_activation),
    (Project, "category", "small", ProjectCategory.small),
    (Project, "category", "medium", ProjectCategory.medium),
    (Project, "category", "large", ProjectCategory.large),
    (Release, "impact", "none", ReleaseImpact.none),
    (RequestTemplate, "category", "order", RequestTemplateCategory.order),
    (RequestTemplate, "category", "fulfillment", RequestTemplateCategory.fulfillment),
    (Risk, "status", "anticipated", RiskStatus.anticipated),
    (Risk, "status", "materialized", RiskStatus.materialized),
    (Risk, "status", "closed", RiskStatus.closed),
    (ServiceInstance, "status", "being_prepared", ServiceInstanceStatus.being_prepared),
    (ServiceInstance, "status", "in_production", ServiceInstanceStatus.in_production),
    (ServiceOffering, "status", "planned", ServiceOfferingStatus.planned),
    (ServiceOffering, "status", "unpublished", ServiceOfferingStatus.unpublished),
    (ServiceOffering, "status", "discontinued", ServiceOfferingStatus.discontinued),
])
def test_api_values_become_enum_members(connection, cls, field, value, member):
    record = cls.from_data(connection, {"id": 1, field: value})
    assert getattr(record, field) is member


@pytest.mark.parametrize("enum_cls, value", [
    (ContractStatus, "being_created"),
    (ProblemStatus, "registered"),
    (ProjectStatus, "being_created"),
    (ReleaseStatus, "being_created"),
    (ServiceInstanceStatus, "being_created"),
    (ServiceInstanceStatus, "active"),
    (ServiceOfferingStatus, "not_offered"),
    (RiskStatus, "technology"),
])
def test_values_the_api_does_not_have_are_gone(enum_cls, value):
    assert value not in {m.value for m in enum_cls}


def test_problem_and_project_with_unknown_account_category_still_load(connection):
    # Project categories are defined per account: other references stay text
    assert Project.from_data(connection, {"id": 1, "category": "strategic"}).category == "strategic"
    assert Problem.from_data(connection, {"id": 1, "status": "assigned"}).status is ProblemStatus.assigned
