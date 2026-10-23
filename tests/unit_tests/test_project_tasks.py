import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.project_tasks import ProjectTask, ProjectTaskPredefinedFilter, ProjectTaskStatus


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def project_task_instance(mock_connection):
    return ProjectTask(
        connection_object=mock_connection,
        id=101,
        subject="Prepare test environment",
        status="assigned",
        category="activity",
        project={"id": 40, "subject": "Cloud Migration"},
        manager={"id": 5, "name": "Manager"},
        team={"id": 3, "name": "Operations"},
    )


def test_project_task_initialization(project_task_instance):
    assert isinstance(project_task_instance, ProjectTask)
    assert project_task_instance.__resourceUrl__ == "project_tasks"
    assert project_task_instance.id == 101
    assert project_task_instance.status == ProjectTaskStatus.assigned
    assert isinstance(project_task_instance.manager, Person)
    assert project_task_instance.manager.name == "Manager"
    assert isinstance(project_task_instance.team, Team)
    assert project_task_instance.project == {"id": 40, "subject": "Cloud Migration"}


def test_project_task_keeps_unknown_status(mock_connection):
    task = ProjectTask.from_data(mock_connection, {"id": 1, "status": "some_future_status"})
    assert task.status == "some_future_status"


def test_project_task_from_data_validation(mock_connection):
    with pytest.raises(TypeError):
        ProjectTask.from_data(mock_connection, [])
    with pytest.raises(ValueError):
        ProjectTask.from_data(mock_connection, {"subject": "no id"})


def test_project_task_str(project_task_instance):
    assert str(project_task_instance) == (
        "ProjectTask(id=101, subject=Prepare test environment, status=assigned, category=activity)"
    )
    assert project_task_instance.ref_str() == "ProjectTask(id=101, subject=Prepare test environment)"


def test_get_project_task_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 101, "subject": "Prepare test environment"}
    result = ProjectTask.get_by_id(mock_connection, 101)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks/101", "GET"
    )
    assert isinstance(result, ProjectTask)
    assert result.id == 101


def test_get_project_tasks(mock_connection):
    mock_connection.api_call.return_value = [{"id": 1}, {"id": 2}]
    results = ProjectTask.get_project_tasks(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks", "GET"
    )
    assert [r.id for r in results] == [1, 2]
    assert all(isinstance(r, ProjectTask) for r in results)


def test_get_project_tasks_with_filter_and_limit(mock_connection):
    mock_connection.api_call.return_value = []
    ProjectTask.get_project_tasks(
        mock_connection, predefinedFilter=ProjectTaskPredefinedFilter.assigned_to_me, max_results=10
    )
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks/assigned_to_me", "GET", max_results=10
    )


def test_get_project_tasks_with_queryfilter(mock_connection):
    mock_connection.create_filter_string.return_value = "status=assigned"
    mock_connection.api_call.return_value = []
    ProjectTask.get_project_tasks(mock_connection, queryfilter={"status": "assigned"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks?status=assigned", "GET"
    )


def test_update_project_task(mock_connection, project_task_instance):
    mock_connection.api_call.return_value = {"id": 101, "status": "accepted"}
    result = project_task_instance.update({"status": "accepted"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks/101", "PATCH", {"status": "accepted"}
    )
    assert result.status == "accepted"


def test_update_project_task_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 7, "status": "accepted"}
    result = ProjectTask.update_by_id(mock_connection, 7, {"status": "accepted"})
    assert isinstance(result, ProjectTask)
    assert result.id == 7


def test_get_project_task_notes(mock_connection, project_task_instance):
    mock_connection.api_call.return_value = [{"id": 11, "text": "note"}]
    notes = project_task_instance.get_notes()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks/101/notes", "GET"
    )
    assert notes == [{"id": 11, "text": "note"}]


def test_add_project_task_note_text(mock_connection, project_task_instance):
    mock_connection.api_call.return_value = {"id": 1, "text": "Hello"}
    project_task_instance.add_note("Hello")
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks/101/notes", "POST", {"text": "Hello"}
    )


def test_add_project_task_note_dict(mock_connection, project_task_instance):
    note = {"text": "Hello", "suppress_note_added_notifications": True}
    project_task_instance.add_note(note)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks/101/notes", "POST", note
    )


def test_add_project_task_note_invalid_type(project_task_instance):
    with pytest.raises(TypeError):
        project_task_instance.add_note(42)
