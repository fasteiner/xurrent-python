import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import os
import sys
from requests.exceptions import HTTPError
from dotenv import load_dotenv

# Add the `../src` directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.requests import Request, CompletionReason, PredefinedFilter, PredefinedNotesFilter
from xurrent.core import XurrentApiHelper
from xurrent.teams import Team
from xurrent.people import Person
from xurrent.workflows import Workflow

# FILE: src/xurrent/test_requests.py

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


def test_integration(x_api_helper):
    # Create a new request
    new_request = Request.create(
        connection_object=x_api_helper,
        data={
            "subject": "Integration Test Request",
            "category": "other",
            "subject": "Integration Test Request"
        }
    )

    assert isinstance(new_request, Request)
    assert new_request.subject == "Integration Test Request"
    assert new_request.category == "other"

    # write a note
    note_data = {"text": "Integration Test Note", "internal": True}
    new_note = new_request.add_note(note_data)
    # print("new note: ",new_note)
    last_note = new_request.get_note_by_id(new_note["id"])
    # print("last note: ",last_note)
    # print("last note text: ",last_note["text"])
    assert last_note["text"] == "Integration Test Note"
    assert last_note["person"]["id"] == x_api_helper.api_user.id

    # try archiving the request (should fail)
    with pytest.raises(HTTPError):
        new_request.archive()

    # close the request
    closed_request = new_request.close("Integration Test Close", CompletionReason.solved)
    assert closed_request.status == "completed"
    assert closed_request.completion_reason == "solved"
    assert hasattr(closed_request, "archived") == False
    assert hasattr(closed_request, "trashed") == False
    assert closed_request.member.id == x_api_helper.api_user.id
    assert closed_request.team.id == x_api_helper.api_user_teams[0].id

    # archive the request
    archived_request = closed_request.archive()
    assert hasattr(archived_request, "archived") == True
    assert archived_request.archived == True

    #restore the request
    restored_request = archived_request.restore()
    if hasattr(restored_request, "archived"):
        assert restored_request.archived == False
    else:
        assert hasattr(restored_request, "archived") == False

    # trash the request
    trashed_request = restored_request.trash()
    assert hasattr(trashed_request, "trashed") == True
    assert trashed_request.trashed == True
