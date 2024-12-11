import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import os
import sys
from requests.exceptions import HTTPError

# Add the `../src` directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.requests import Request, CompletionReason, PredefinedFilter, PredefinedNotesFilter
from xurrent.core import XurrentApiHelper
from xurrent.teams import Team
from xurrent.people import Person
from xurrent.workflows import Workflow

# FILE: src/xurrent/test_requests.py


@pytest.fixture
def mock_connection():
    magicMock= MagicMock(spec=XurrentApiHelper)
    magicMock.base_url = "https://api.example.com"
    magicMock.api_user = Person(connection_object=magicMock, id=1, name="api_user")
    magicMock.api_user_teams = [Team(connection_object=magicMock, id=1, name="api_user_team")]
    return magicMock


@pytest.fixture
def request_instance(mock_connection):
    return Request(
        connection_object=mock_connection,
        id=1,
        source="source",
        sourceID="sourceID",
        subject="subject",
        category="rfc",
        impact="impact",
        status="status",
        next_target_at=datetime.now(),
        completed_at=datetime.now(),
        team=Team(connection_object=mock_connection,id=1876789, name="team"),
        member=Person(connection_object=mock_connection,id=1, name="member"),
        grouped_into=2,
        service_instance={"name": "service_instance"},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        workflow=Workflow(connection_object=mock_connection,id=1, subject="workflow"),
        requested_by=Person(connection_object=mock_connection,id=2, name="requested_by"),
        requested_for=Person(connection_object=mock_connection,id=3, name="requested_for"),
        created_by=Person(connection_object=mock_connection,id=4, name="created_by")
    )

def test_request_initialization(request_instance):
    assert isinstance(request_instance, Request)
    assert request_instance.__resourceUrl__ == "requests"
    assert request_instance.id == 1
    assert request_instance.subject == "subject"
    assert isinstance(request_instance.member, Person)
    assert request_instance.member.name == "member"
    assert isinstance(request_instance.requested_by, Person)
    assert request_instance.requested_by.name == "requested_by"
    assert isinstance(request_instance.requested_for, Person)
    assert request_instance.requested_for.name == "requested_for"
    assert isinstance(request_instance.created_by, Person)
    assert request_instance.created_by.name == "created_by"
    assert isinstance(request_instance.workflow, Workflow)
    assert request_instance.workflow.subject == "workflow"

def test_to_json(request_instance):
    json_data = request_instance.to_json()
    assert type(json_data) == str

def test_to_string(request_instance):
    workflow_ref = request_instance.workflow.ref_str()
    created_by_ref = request_instance.created_by.ref_str()
    assert str(request_instance) == f"Request(id=1, subject=subject, category=rfc, status=status, impact=impact, created_by={created_by_ref}, workflow={workflow_ref})"

    request_instance.workflow = None
    request_instance.created_by = None
    assert str(request_instance) == "Request(id=1, subject=subject, category=rfc, status=status, impact=impact)"


def test_request_from_data(mock_connection):
    request_data = {
        "id": 1,
        "source": "source",
        "sourceID": "sourceID",
        "subject": "subject",
        "category": "rfc",
        "impact": "impact",
        "status": "status",
        "next_target_at": datetime.now(),
        "completed_at": datetime.now(),
        "team": {"id":1876789,"name": "team"},
        "member": {"id": 1, "name": "member"},
        "grouped_into": 2,
        "service_instance": {"name": "service_instance"},
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "workflow": {"id": 1, "subject": "workflow"},
        "requested_by": {"id": 2, "name": "requested_by"},
        "requested_for": {"id": 3, "name": "requested_for"},
        "created_by": {"id": 4, "name": "created_by"}
    }
    request = Request.from_data(mock_connection, request_data)
    assert isinstance(request, Request)
    assert request.id == 1
    assert request.subject == "subject"
    assert isinstance(request.member, Person)
    assert request.member.name == "member"
    assert isinstance(request.requested_by, Person)
    assert request.requested_by.name == "requested_by"
    assert isinstance(request.requested_for, Person)
    assert request.requested_for.name == "requested_for"
    assert isinstance(request.created_by, Person)
    assert request.created_by.name == "created_by"
    assert isinstance(request.workflow, Workflow)
    assert request.workflow.subject == "workflow"
    assert request.team.name == "team"
    assert isinstance(request.team, Team)


def test_get_request_by_id(mock_connection):
    resource_id = 123
    subject = "Test subject"
    mock_response = {'id': resource_id, 'subject': subject}
    mock_connection.api_call.return_value = mock_response
    
    
    # Act
    result = Request.get_by_id(connection_object=mock_connection, id=resource_id)

    # Assert
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/{resource_id}", "GET"
    )
    assert isinstance(result, Request)  # Ensure the result is of type `Request`
    assert result.id == resource_id  # Ensure the ID matches the expected value
    assert result.subject == subject  # Ensure the subject matches the expected value


def test_request_add_note_string(mock_connection, request_instance):
    note_text = "This is a test note."
    mock_connection.api_call.return_value = {"id": 1, "text": note_text}

    response = request_instance.add_note(note_text)

    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/{request_instance.id}/notes", "POST", {"text": note_text}
    )

    assert response["text"] == note_text

def test_request_add_note_dict(mock_connection, request_instance):
    note_data = {"text": "This is a test note.", "internal": True}
    note_data_response = note_data.copy()
    note_data_response["id"] = 1
    mock_connection.api_call.return_value = note_data_response

    response = request_instance.add_note(note_data)

    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/{request_instance.id}/notes", "POST", note_data
    )

    assert response == note_data_response

def test_request_get_notes(mock_connection, request_instance):
    notes_data = [{"id": 1, "text": "Note 1"}, {"id": 2, "text": "Note 2"}]
    mock_connection.api_call.return_value = notes_data

    response = request_instance.get_notes()

    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/{request_instance.id}/notes", "GET"
    )

    assert response == notes_data

def test_request_get_note_by_id(mock_connection, request_instance):
    note_id = 123
    note_data = {"id": note_id, "text": "Specific Note"}
    mock_connection.api_call.return_value = [note_data]

    response = request_instance.get_note_by_id(note_id)
    
    assert response == note_data


def test_request_close(mock_connection, request_instance):
    mock_connection.api_call.return_value = {
        "id": 1,
        "status": "completed",
        "completion_reason": "solved"
    }

    response = request_instance.close(note="Closing test", completion_reason=CompletionReason.solved)

    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/{request_instance.id}", "PATCH",
        {"status": "completed", "completion_reason": "solved", "note": "Closing test", "member_id": mock_connection.api_user.id, "team_id": mock_connection.api_user_teams[0].id}
    )

    assert isinstance(response, Request)
    assert response.status == "completed"
    assert response.completion_reason == "solved"

def test_request_close_and_trash(mock_connection, request_instance):
    mock_connection.api_call.side_effect = [
        {"status": "completed", "completion_reason": "solved", "id": request_instance.id, "trashed": False},
        {"status": "completed", "completion_reason": "solved", "id": request_instance.id, "trashed": True}
    ]

    response = request_instance.close_and_trash(note="Closing and trashing test")

    assert mock_connection.api_call.call_count == 2

    close_call = mock_connection.api_call.call_args_list[0]
    trash_call = mock_connection.api_call.call_args_list[1]

    assert isinstance(response, Request)
    assert close_call.args[1] == "PATCH"
    assert trash_call.args[1] == "POST"
    assert response.status == "completed"
    assert response.trashed == True


def test_request_archive(mock_connection, request_instance):
    mock_connection.api_call.return_value = {"status": "completed", "id": request_instance.id, "archived": True}

    response = request_instance.archive()

    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/{request_instance.id}/archive", "POST"
    )

    assert isinstance(response, Request)
    assert response.archived == True

def test_request_restore(mock_connection, request_instance):
    request_instance.archived = True
    mock_connection.api_call.return_value = {"archived": False, "trashed": False, "id": request_instance.id}

    response = request_instance.restore()

    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/{request_instance.id}/restore", "POST"
    )

    assert isinstance(response, Request)
    assert response.archived == False
    assert response.trashed == False

def test_request_trash(mock_connection, request_instance):
    request_instance.trashed = False
    mock_connection.api_call.return_value = {"status": "completed", "id": request_instance.id, "trashed": True}

    response = request_instance.trash()

    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/requests/{request_instance.id}/trash", "POST"
    )

    assert isinstance(response, Request)
    assert response.trashed == True

