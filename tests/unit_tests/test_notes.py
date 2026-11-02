import os
import sys
from unittest.mock import MagicMock

import pytest
import requests

# Add the `../src` directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.problems import Problem
from xurrent.project_tasks import ProjectTask
from xurrent.projects import Project
from xurrent.releases import Release
from xurrent.requests import Request, PredefinedNotesFilter
from xurrent.tasks import Task
from xurrent.workflows import Workflow

BASE = "https://api.example.com/v1"

RECORD_CLASSES = [
    (Request, "requests"),
    (Task, "tasks"),
    (Problem, "problems"),
    (ProjectTask, "project_tasks"),
    (Workflow, "workflows"),
    (Project, "projects"),
    (Release, "releases"),
]


@pytest.fixture
def connection():
    """A real helper (filter strings are built for real) whose api_call is mocked."""
    helper = XurrentApiHelper(BASE, "api_key", "account", False)
    helper.api_call = MagicMock(return_value=[{"id": 1, "text": "note"}])
    return helper


@pytest.mark.parametrize("cls, resource", RECORD_CLASSES)
def test_get_notes_without_options_is_unchanged(connection, cls, resource):
    assert cls(connection, 5).get_notes() == [{"id": 1, "text": "note"}]
    connection.api_call.assert_called_once_with(f"{BASE}/{resource}/5/notes", "GET")


@pytest.mark.parametrize("cls, resource", RECORD_CLASSES)
def test_get_notes_newest_first_reads_one_note(connection, cls, resource):
    cls(connection, 5).get_notes(sort="-created_at", max_results=1)
    connection.api_call.assert_called_once_with(
        f"{BASE}/{resource}/5/notes?sort=-created_at", "GET", max_results=1
    )


@pytest.mark.parametrize("cls, resource", RECORD_CLASSES)
def test_get_notes_with_filter_and_sort(connection, cls, resource):
    cls(connection, 5).get_notes(queryfilter={"medium": "email"}, sort="-created_at,-id")
    connection.api_call.assert_called_once_with(
        f"{BASE}/{resource}/5/notes?medium=email&sort=-created_at,-id", "GET"
    )


def test_request_get_notes_with_predefined_filter_and_sort(connection):
    Request(connection, 5).get_notes(PredefinedNotesFilter.internal, sort="-created_at", max_results=3)
    connection.api_call.assert_called_once_with(
        f"{BASE}/requests/5/notes/internal?sort=-created_at", "GET", max_results=3
    )


def test_get_notes_sort_is_url_encoded(connection):
    Task(connection, 5).get_notes(sort="created_at&x=1")
    connection.api_call.assert_called_once_with(f"{BASE}/tasks/5/notes?sort=created_at%26x%3D1", "GET")


def test_newest_note_is_one_call_with_per_page_1(monkeypatch):
    """Only the first page is read, even though the API offers a next page."""
    calls = []

    def fake_request(method, url, headers=None, json=None):
        calls.append(url)
        response = MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = [{"id": 42, "text": "newest"}]
        response.headers = {"Link": f'<{BASE}/requests/5/notes?sort=-created_at&per_page=1&search_after=x>; rel="next"'}
        return response

    monkeypatch.setattr(requests, "request", fake_request)
    helper = XurrentApiHelper(BASE, "api_key", "account", False)
    notes = Request(helper, 5).get_notes(sort="-created_at", max_results=1)
    assert notes == [{"id": 42, "text": "newest"}]
    assert calls == [f"{BASE}/requests/5/notes?sort=-created_at&per_page=1"]
