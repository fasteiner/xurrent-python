import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.problems import Problem, ProblemPredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def problem_instance(mock_connection):
    return Problem(
        connection_object=mock_connection,
        id=10,
        subject="Server crash",
        status="in_progress",
        impact="high",
        manager=Person(connection_object=mock_connection, id=5, name="Manager"),
        team=Team(connection_object=mock_connection, id=2, name="Ops"),
    )


def test_problem_initialization(problem_instance):
    assert isinstance(problem_instance, Problem)
    assert problem_instance.__resourceUrl__ == "problems"
    assert problem_instance.id == 10
    assert problem_instance.subject == "Server crash"
    assert isinstance(problem_instance.manager, Person)
    assert problem_instance.manager.name == "Manager"
    assert isinstance(problem_instance.team, Team)
    assert problem_instance.team.name == "Ops"


def test_problem_from_data(mock_connection):
    data = {
        "id": 10,
        "subject": "Server crash",
        "status": "in_progress",
        "impact": "high",
        "manager": {"id": 5, "name": "Manager"},
        "team": {"id": 2, "name": "Ops"},
    }
    problem = Problem.from_data(mock_connection, data)
    assert isinstance(problem, Problem)
    assert problem.id == 10
    assert isinstance(problem.manager, Person)
    assert isinstance(problem.team, Team)


def test_get_problem_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 10, "subject": "Server crash"}
    result = Problem.get_by_id(mock_connection, 10)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems/10", "GET"
    )
    assert isinstance(result, Problem)
    assert result.id == 10


def test_get_problems(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "subject": "Problem A"},
        {"id": 2, "subject": "Problem B"},
    ]
    results = Problem.get_problems(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Problem) for r in results)


def test_get_problems_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    Problem.get_problems(mock_connection, predefinedFilter=ProblemPredefinedFilter.active)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems/active", "GET"
    )


def test_create_problem(mock_connection):
    mock_connection.api_call.return_value = {"id": 11, "subject": "New Problem"}
    result = Problem.create(mock_connection, {"subject": "New Problem"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems", "POST", {"subject": "New Problem"}
    )
    assert isinstance(result, Problem)
    assert result.id == 11


def test_update_problem(mock_connection, problem_instance):
    mock_connection.api_call.return_value = {"id": 10, "subject": "Updated Problem"}
    result = problem_instance.update({"subject": "Updated Problem"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems/10", "PATCH", {"subject": "Updated Problem"}
    )
    assert isinstance(result, Problem)
    assert result.subject == "Updated Problem"


def test_archive_problem(mock_connection, problem_instance):
    mock_connection.api_call.return_value = {"id": 10, "subject": "Server crash"}
    result = problem_instance.archive()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems/10/archive", "POST"
    )
    assert isinstance(result, Problem)


def test_trash_problem(mock_connection, problem_instance):
    mock_connection.api_call.return_value = {"id": 10, "subject": "Server crash"}
    result = problem_instance.trash()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems/10/trash", "POST"
    )
    assert isinstance(result, Problem)


def test_restore_problem(mock_connection, problem_instance):
    mock_connection.api_call.return_value = {"id": 10, "subject": "Server crash"}
    result = problem_instance.restore()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems/10/restore", "POST"
    )
    assert isinstance(result, Problem)


def test_get_notes(mock_connection, problem_instance):
    notes_data = [{"id": 1, "text": "Note 1"}, {"id": 2, "text": "Note 2"}]
    mock_connection.api_call.return_value = notes_data
    result = problem_instance.get_notes()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems/10/notes", "GET"
    )
    assert result == notes_data


def test_add_note_string(mock_connection, problem_instance):
    mock_connection.api_call.return_value = {"id": 1, "text": "A note"}
    problem_instance.add_note("A note")
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems/10/notes", "POST", {"text": "A note"}
    )


def test_add_note_dict(mock_connection, problem_instance):
    note = {"text": "A note", "internal": True}
    mock_connection.api_call.return_value = {"id": 1, **note}
    problem_instance.add_note(note)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems/10/notes", "POST", note
    )


def test_get_requests(mock_connection, problem_instance):
    from xurrent.requests import Request
    mock_connection.api_call.return_value = [
        {"id": 1, "subject": "Req A"},
        {"id": 2, "subject": "Req B"},
    ]
    results = problem_instance.get_requests()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems/10/requests", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Request) for r in results)


def test_get_workflows(mock_connection, problem_instance):
    from xurrent.workflows import Workflow
    mock_connection.api_call.return_value = [
        {"id": 1, "subject": "Wf A"},
        {"id": 2, "subject": "Wf B"},
    ]
    results = problem_instance.get_workflows()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/problems/10/workflows", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Workflow) for r in results)
