import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.projects import Project, ProjectPredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def project_instance(mock_connection):
    return Project(
        connection_object=mock_connection,
        id=40,
        subject="Cloud Migration",
        status="in_progress",
        category="migration",
        manager=Person(connection_object=mock_connection, id=5, name="Manager"),
    )


def test_project_initialization(project_instance):
    assert isinstance(project_instance, Project)
    assert project_instance.__resourceUrl__ == "projects"
    assert project_instance.id == 40
    assert project_instance.subject == "Cloud Migration"
    assert isinstance(project_instance.manager, Person)
    assert project_instance.manager.name == "Manager"


def test_project_from_data(mock_connection):
    data = {
        "id": 40,
        "subject": "Cloud Migration",
        "status": "in_progress",
        "category": "migration",
        "manager": {"id": 5, "name": "Manager"},
    }
    project = Project.from_data(mock_connection, data)
    assert isinstance(project, Project)
    assert project.id == 40
    assert isinstance(project.manager, Person)


def test_get_project_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 40, "subject": "Cloud Migration"}
    result = Project.get_by_id(mock_connection, 40)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects/40", "GET"
    )
    assert isinstance(result, Project)
    assert result.id == 40


def test_get_projects(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "subject": "Proj A"},
        {"id": 2, "subject": "Proj B"},
    ]
    results = Project.get_projects(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Project) for r in results)


def test_get_projects_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    Project.get_projects(mock_connection, predefinedFilter=ProjectPredefinedFilter.open)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects/open", "GET"
    )


def test_create_project(mock_connection):
    mock_connection.api_call.return_value = {"id": 41, "subject": "New Project"}
    result = Project.create(mock_connection, {"subject": "New Project"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects", "POST", {"subject": "New Project"}
    )
    assert isinstance(result, Project)
    assert result.id == 41


def test_update_project(mock_connection, project_instance):
    mock_connection.api_call.return_value = {"id": 40, "subject": "Updated Project"}
    result = project_instance.update({"subject": "Updated Project"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects/40", "PATCH", {"subject": "Updated Project"}
    )
    assert isinstance(result, Project)
    assert result.subject == "Updated Project"


def test_archive_project(mock_connection, project_instance):
    mock_connection.api_call.return_value = {"id": 40, "subject": "Cloud Migration"}
    result = project_instance.archive()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects/40/archive", "POST"
    )
    assert isinstance(result, Project)


def test_trash_project(mock_connection, project_instance):
    mock_connection.api_call.return_value = {"id": 40, "subject": "Cloud Migration"}
    result = project_instance.trash()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects/40/trash", "POST"
    )
    assert isinstance(result, Project)


def test_restore_project(mock_connection, project_instance):
    mock_connection.api_call.return_value = {"id": 40, "subject": "Cloud Migration"}
    result = project_instance.restore()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects/40/restore", "POST"
    )
    assert isinstance(result, Project)


def test_get_tasks(mock_connection, project_instance):
    from xurrent.tasks import Task
    mock_connection.api_call.return_value = [
        {"id": 1, "subject": "Task A"},
        {"id": 2, "subject": "Task B"},
    ]
    results = project_instance.get_tasks()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects/40/tasks", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Task) for r in results)


def test_get_phases(mock_connection, project_instance):
    phases_data = [{"id": 1, "name": "Phase 1"}, {"id": 2, "name": "Phase 2"}]
    mock_connection.api_call.return_value = phases_data
    result = project_instance.get_phases()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects/40/phases", "GET"
    )
    assert result == phases_data


def test_get_workflows(mock_connection, project_instance):
    from xurrent.workflows import Workflow
    mock_connection.api_call.return_value = [{"id": 1, "subject": "Wf A"}]
    results = project_instance.get_workflows()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects/40/workflows", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Workflow) for r in results)


def test_get_notes(mock_connection, project_instance):
    notes_data = [{"id": 1, "text": "Note 1"}]
    mock_connection.api_call.return_value = notes_data
    result = project_instance.get_notes()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects/40/notes", "GET"
    )
    assert result == notes_data


def test_add_note_string(mock_connection, project_instance):
    mock_connection.api_call.return_value = {"id": 1, "text": "A note"}
    project_instance.add_note("A note")
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/projects/40/notes", "POST", {"text": "A note"}
    )
