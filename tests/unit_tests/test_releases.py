import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.releases import Release, ReleasePredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def release_instance(mock_connection):
    return Release(
        connection_object=mock_connection,
        id=50,
        subject="v2.0 Release",
        status="in_progress",
        impact="medium",
        manager=Person(connection_object=mock_connection, id=5, name="Manager"),
    )


def test_release_initialization(release_instance):
    assert isinstance(release_instance, Release)
    assert release_instance.__resourceUrl__ == "releases"
    assert release_instance.id == 50
    assert release_instance.subject == "v2.0 Release"
    assert isinstance(release_instance.manager, Person)
    assert release_instance.manager.name == "Manager"


def test_release_from_data(mock_connection):
    data = {
        "id": 50,
        "subject": "v2.0 Release",
        "status": "in_progress",
        "impact": "medium",
        "manager": {"id": 5, "name": "Manager"},
    }
    release = Release.from_data(mock_connection, data)
    assert isinstance(release, Release)
    assert release.id == 50
    assert isinstance(release.manager, Person)


def test_get_release_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 50, "subject": "v2.0 Release"}
    result = Release.get_by_id(mock_connection, 50)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases/50", "GET"
    )
    assert isinstance(result, Release)
    assert result.id == 50


def test_get_releases(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "subject": "v1.0"},
        {"id": 2, "subject": "v2.0"},
    ]
    results = Release.get_releases(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Release) for r in results)


def test_get_releases_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    Release.get_releases(mock_connection, predefinedFilter=ReleasePredefinedFilter.open)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases/open", "GET"
    )


def test_create_release(mock_connection):
    mock_connection.api_call.return_value = {"id": 51, "subject": "v3.0"}
    result = Release.create(mock_connection, {"subject": "v3.0"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases", "POST", {"subject": "v3.0"}
    )
    assert isinstance(result, Release)
    assert result.id == 51


def test_update_release(mock_connection, release_instance):
    mock_connection.api_call.return_value = {"id": 50, "subject": "v2.1 Release"}
    result = release_instance.update({"subject": "v2.1 Release"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases/50", "PATCH", {"subject": "v2.1 Release"}
    )
    assert isinstance(result, Release)
    assert result.subject == "v2.1 Release"


def test_archive_release(mock_connection, release_instance):
    mock_connection.api_call.return_value = {"id": 50, "subject": "v2.0 Release"}
    result = release_instance.archive()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases/50/archive", "POST"
    )
    assert isinstance(result, Release)


def test_trash_release(mock_connection, release_instance):
    mock_connection.api_call.return_value = {"id": 50, "subject": "v2.0 Release"}
    result = release_instance.trash()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases/50/trash", "POST"
    )
    assert isinstance(result, Release)


def test_restore_release(mock_connection, release_instance):
    mock_connection.api_call.return_value = {"id": 50, "subject": "v2.0 Release"}
    result = release_instance.restore()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases/50/restore", "POST"
    )
    assert isinstance(result, Release)


def test_get_workflows(mock_connection, release_instance):
    from xurrent.workflows import Workflow
    mock_connection.api_call.return_value = [
        {"id": 1, "subject": "Wf A"},
        {"id": 2, "subject": "Wf B"},
    ]
    results = release_instance.get_workflows()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases/50/workflows", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Workflow) for r in results)


def test_get_notes(mock_connection, release_instance):
    notes_data = [{"id": 1, "text": "Note 1"}]
    mock_connection.api_call.return_value = notes_data
    result = release_instance.get_notes()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases/50/notes", "GET"
    )
    assert result == notes_data


def test_add_note_string(mock_connection, release_instance):
    mock_connection.api_call.return_value = {"id": 1, "text": "Hello"}
    release_instance.add_note("Hello")
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases/50/notes", "POST", {"text": "Hello"}
    )


def test_add_note_dict(mock_connection, release_instance):
    note = {"text": "Hello", "internal": True}
    mock_connection.api_call.return_value = {"id": 1, **note}
    release_instance.add_note(note)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/releases/50/notes", "POST", note
    )
