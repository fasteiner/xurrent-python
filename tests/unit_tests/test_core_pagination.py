import os
import sys
from unittest.mock import MagicMock

import pytest
import requests

# Add the `../src` directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.knowledge_articles import KnowledgeArticle
from xurrent.problems import Problem
from xurrent.requests import Request, PredefinedNotesFilter
from xurrent.tasks import Task, TaskPredefinedFilter
from xurrent.people import PeoplePredefinedFilter
from xurrent.teams import TeamPredefinedFilter
from xurrent.workflows import WorkflowPredefinedFilter
from xurrent.configuration_items import ConfigurationItemPredefinedFilter

BASE = "https://api.example.com/v1"


def make_response(items, next_url=None):
    response = MagicMock()
    response.status_code = 200
    response.ok = True
    response.json.return_value = items
    response.headers = {"Link": f'<{next_url}>; rel="next"'} if next_url else {}
    return response


@pytest.fixture
def helper():
    return XurrentApiHelper(BASE, "api_key", "account", False)


@pytest.fixture
def fake_api(monkeypatch):
    """Serve pages from a dict url -> response and record the requested urls."""
    pages = {}
    calls = []

    def fake_request(method, url, headers=None, json=None):
        calls.append(url)
        return pages[url]

    monkeypatch.setattr(requests, "request", fake_request)
    return pages, calls


def test_without_max_results_all_pages_are_fetched(helper, fake_api):
    pages, calls = fake_api
    pages[f"{BASE}/requests?per_page=100"] = make_response([{"id": 1}, {"id": 2}], f"{BASE}/requests?page=2&per_page=100")
    pages[f"{BASE}/requests?page=2&per_page=100"] = make_response([{"id": 3}])
    assert [r["id"] for r in helper.api_call("/requests")] == [1, 2, 3]
    assert len(calls) == 2


def test_max_results_stops_paginating_and_truncates(helper, fake_api):
    pages, calls = fake_api
    pages[f"{BASE}/requests?per_page=2"] = make_response([{"id": 1}, {"id": 2}], f"{BASE}/requests?page=2&per_page=2")
    pages[f"{BASE}/requests?page=2&per_page=2"] = make_response([{"id": 3}, {"id": 4}], f"{BASE}/requests?page=3&per_page=2")
    result = helper.api_call("/requests", per_page=2, max_results=3)
    assert [r["id"] for r in result] == [1, 2, 3]
    assert calls == [f"{BASE}/requests?per_page=2", f"{BASE}/requests?page=2&per_page=2"]


def test_max_results_reduces_page_size(helper, fake_api):
    pages, calls = fake_api
    pages[f"{BASE}/requests?per_page=5"] = make_response([{"id": i} for i in range(5)], f"{BASE}/next")
    assert len(helper.api_call("/requests", max_results=5)) == 5
    assert calls == [f"{BASE}/requests?per_page=5"]


def test_max_results_must_be_positive(helper):
    with pytest.raises(ValueError):
        helper.api_call("/requests", max_results=0)


def test_repeated_page_ends_pagination(helper, fake_api):
    """/search keeps sending a 'next' link that returns the same results again."""
    pages, calls = fake_api
    results = [{"id": 20, "type": "knowledge-article"}, {"id": 22, "type": "knowledge-article"}]
    pages[f"{BASE}/search?q=printer&per_page=100"] = make_response(results, f"{BASE}/search?q=printer&per_page=100&page=a")
    pages[f"{BASE}/search?q=printer&per_page=100&page=a"] = make_response(results, f"{BASE}/search?q=printer&per_page=100&page=b")
    assert helper.api_call("/search?q=printer") == results
    assert len(calls) == 2


def test_pages_with_new_records_continue(helper, fake_api):
    pages, calls = fake_api
    pages[f"{BASE}/search?q=x&per_page=100"] = make_response([{"id": 1, "type": "request"}], f"{BASE}/search?q=x&per_page=100&page=a")
    pages[f"{BASE}/search?q=x&per_page=100&page=a"] = make_response([{"id": 1, "type": "request"}, {"id": 1, "type": "task"}])
    result = helper.api_call("/search?q=x")
    assert result == [{"id": 1, "type": "request"}, {"id": 1, "type": "request"}, {"id": 1, "type": "task"}]


def test_search_with_max_results():
    helper = XurrentApiHelper("https://api.example.com", "api_key", "account", False)
    helper.api_call = MagicMock(return_value=[])
    helper.search("printer", types=["knowledge-article"], max_results=10)
    helper.api_call.assert_called_once_with("/search?q=printer&types=knowledge-article", "GET", max_results=10)


@pytest.mark.parametrize("cls, method", [
    (Request, "get_requests"),
    (Task, "get_tasks"),
    (Problem, "get_problems"),
    (KnowledgeArticle, "get_knowledge_articles"),
])
def test_list_methods_pass_max_results(cls, method):
    connection = MagicMock(spec=XurrentApiHelper)
    connection.base_url = "https://api.example.com"
    connection.api_call.return_value = [{"id": 1}]
    result = getattr(cls, method)(connection, max_results=25)
    assert connection.api_call.call_args.kwargs == {"max_results": 25}
    assert isinstance(result[0], cls)


@pytest.mark.parametrize("member, value", [
    (TaskPredefinedFilter.assigned_to_me, "assigned_to_me"),
    (PredefinedNotesFilter.internal, "internal"),
    (PeoplePredefinedFilter.enabled, "enabled"),
    (TeamPredefinedFilter.enabled, "enabled"),
    (WorkflowPredefinedFilter.managed_by_me, "managed_by_me"),
    (ConfigurationItemPredefinedFilter.active, "active"),
])
def test_predefined_filters_format_as_value(member, value):
    # Python 3.12+ would otherwise render "TaskPredefinedFilter.assigned_to_me" in URLs
    assert f"/x/{member}" == f"/x/{value}"


def test_task_filter_url():
    connection = MagicMock(spec=XurrentApiHelper)
    connection.base_url = "https://api.example.com"
    connection.api_call.return_value = []
    Task.get_tasks(connection, predefinedFilter=TaskPredefinedFilter.assigned_to_me)
    connection.api_call.assert_called_once_with("https://api.example.com/tasks/assigned_to_me", "GET")


def test_request_notes_filter_url():
    connection = MagicMock(spec=XurrentApiHelper)
    connection.base_url = "https://api.example.com"
    connection.api_call.return_value = []
    Request(connection, 5).get_notes(predefinedFilter=PredefinedNotesFilter.internal)
    connection.api_call.assert_called_once_with("https://api.example.com/requests/5/notes/internal", "GET")


def test_no_timeout_by_default(fake_api):
    pages, calls = fake_api
    helper = XurrentApiHelper(BASE, "api_key", "account", False)
    assert helper._timeout_kwargs() == {}


def test_timeout_is_passed_to_requests(monkeypatch):
    seen = {}

    def fake_request(method, url, headers=None, json=None, timeout=None):
        seen["timeout"] = timeout
        return make_response({"id": 1})

    monkeypatch.setattr(requests, "request", fake_request)
    helper = XurrentApiHelper(BASE, "api_key", "account", False, timeout=30)
    helper.api_call("/requests/1", per_page=0)
    assert seen["timeout"] == 30
