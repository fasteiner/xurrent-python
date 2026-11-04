"""A value Xurrent added after this SDK (a newer request category, a status) must not stop a
record from loading: known values become the enum member, unknown ones stay plain strings."""

from unittest.mock import MagicMock

from xurrent.core import enum_or_raw
from xurrent.problems import Problem, ProblemStatus
from xurrent.requests import Request, RequestCategory
from xurrent.workflows import Workflow


def test_known_values_become_members():
    assert enum_or_raw(RequestCategory, "rfc") is RequestCategory.rfc
    assert enum_or_raw(ProblemStatus, "accepted") is ProblemStatus.accepted


def test_unknown_values_stay_strings_and_none_stays_none():
    assert enum_or_raw(RequestCategory, "some_new_category") == "some_new_category"
    assert enum_or_raw(RequestCategory, None) is None
    marker = object()
    assert enum_or_raw(RequestCategory, marker) is marker


def test_a_request_with_an_unknown_category_loads():
    request = Request.from_data(MagicMock(), {"id": 1, "category": "some_new_category"})
    assert request.category == "some_new_category"
    known = Request.from_data(MagicMock(), {"id": 2, "category": "incident"})
    assert known.category is RequestCategory.incident


def test_a_problem_with_an_unknown_status_loads():
    problem = Problem.from_data(MagicMock(), {"id": 3, "status": "some_new_status"})
    assert problem.status == "some_new_status"


def test_a_workflow_with_an_unknown_category_loads():
    workflow = Workflow.from_data(MagicMock(), {"id": 4, "category": "some_new_category"})
    assert workflow.category == "some_new_category"
