import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import os
import sys

# Add the `../src` directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from xurrent.requests import Request, CompletionReason, PredefinedFilter, PredefinedNotesFilter
from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.workflows import Workflow

# FILE: src/xurrent/test_requests.py


@pytest.fixture
def mock_connection():
    magicMock= MagicMock(spec=XurrentApiHelper)
    magicMock.base_url = "https://api.example.com"
    return magicMock

@pytest.fixture
def x_api_helper():
    # Retrieve environment variables
    # Load .env file only if the environment variables are not already set
    if not os.getenv("APITOKEN") or not os.getenv("APIACCOUNT") or not os.getenv("APIURL"):
        load_dotenv()
    api_token = os.getenv("APITOKEN")  # Fetches DEMO_API_TOKEN, returns None if not set
    api_account = os.getenv("APIACCOUNT")
    api_url = os.getenv("APIURL")

    # Check if the environment variables are properly set
    if not all([api_token, api_account, api_url]):
        raise EnvironmentError("One or more environment variables are missing.")
    helper = XurrentApiHelper(api_url, api_token, api_account, True)
    return helper

@pytest.fixture
def request_instance(mock_connection):
    return Request(
        connection_object=mock_connection,
        id=1,
        source="source",
        sourceID="sourceID",
        subject="subject",
        category="category",
        impact="impact",
        status="status",
        next_target_at=datetime.now(),
        completed_at=datetime.now(),
        team={"name": "team"},
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
    assert request_instance.resourceUrl == "requests"
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
    assert str(request_instance) == f"Request(id=1, subject=subject, category=category, status=status, impact=impact, created_by={created_by_ref}, workflow={workflow_ref})"


def test_request_from_data(mock_connection):
    request_data = {
        "id": 1,
        "source": "source",
        "sourceID": "sourceID",
        "subject": "subject",
        "category": "category",
        "impact": "impact",
        "status": "status",
        "next_target_at": datetime.now(),
        "completed_at": datetime.now(),
        "team": {"name": "team"},
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
    #TODO: Member, requested_by, requested_for, created_by, workflow are not being converted correctly
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