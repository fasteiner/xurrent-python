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


# ---------------------------------------------------------------- approvals (#50)
# Xurrent has no approvals collection for project tasks: the assignments of an approval
# project task (GET /project_tasks/:id/assignments) are its approvals.

from xurrent.project_tasks import (  # noqa: E402
    PROJECT_TASK_APPROVAL_PENDING,
    ProjectTaskApprovalStatus,
    ProjectTaskAssignmentStatus,
    ProjectTaskCategory,
)


@pytest.fixture
def approval_project_task(mock_connection):
    return ProjectTask(
        connection_object=mock_connection,
        id=202,
        subject="Approve the test plan",
        status="assigned",
        category="approval",
        required_approvals=2,
    )


def _assignment(person_id, status, assignment_id):
    return {
        "id": assignment_id,
        "assignee": {"id": person_id, "name": f"Person {person_id}"},
        "status": status,
        "planned_effort": 15,
    }


def test_required_approvals_is_kept(approval_project_task, mock_connection):
    assert approval_project_task.required_approvals == 2
    task = ProjectTask.from_data(mock_connection, {"id": 3, "category": "activity"})
    assert task.required_approvals is None


def test_get_assignments_reads_all_pages_through_the_helper(mock_connection, project_task_instance):
    rows = [_assignment(1, "assigned", 1), _assignment(2, "accepted", 2)]
    mock_connection.api_call.return_value = rows
    assert project_task_instance.get_assignments() == rows
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks/101/assignments", "GET"
    )


def test_get_assignments_with_limit(mock_connection, project_task_instance):
    mock_connection.api_call.return_value = []
    project_task_instance.get_assignments(max_results=5)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks/101/assignments", "GET", max_results=5
    )


def test_get_assignments_of_an_unexpected_answer_is_empty(mock_connection, project_task_instance):
    mock_connection.api_call.return_value = {"message": "odd"}
    assert project_task_instance.get_assignments() == []


def test_get_approvals_are_the_assignments(mock_connection, approval_project_task):
    rows = [_assignment(1, "approved", 1), _assignment(2, "assigned", 2)]
    mock_connection.api_call.return_value = rows
    assert approval_project_task.get_approvals() == rows
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks/202/assignments", "GET"
    )


def test_get_approvals_without_a_known_category_reads_too(mock_connection):
    mock_connection.api_call.return_value = []
    assert ProjectTask(mock_connection, 9).get_approvals() == []
    mock_connection.api_call.assert_called_once()


def test_get_approvals_of_an_activity_raises(mock_connection, project_task_instance):
    with pytest.raises(ValueError, match="Only approval project tasks"):
        project_task_instance.get_approvals()
    mock_connection.api_call.assert_not_called()


def test_get_approvals_propagates_a_refusal(mock_connection, approval_project_task):
    """401/403 from the API are the helper's HTTPError: passed on, never swallowed."""
    import requests

    mock_connection.api_call.side_effect = requests.HTTPError("403 Client Error")
    with pytest.raises(requests.HTTPError):
        approval_project_task.get_approvals()


def test_get_my_approvals_of_the_api_user(mock_connection, approval_project_task):
    mine = _assignment(1, "approved", 2)
    mock_connection.api_call.return_value = [_assignment(7, "assigned", 1), mine]
    assert approval_project_task.get_my_approvals() == [mine]


def test_get_my_approvals_of_a_given_person_and_several_entries(
    mock_connection, approval_project_task
):
    rows = [
        _assignment(7, "approved", 1),
        _assignment(8, "assigned", 2),
        _assignment(7, "assigned", 3),
        {"id": 4, "status": "assigned"},  # no assignee
        {"id": 5, "assignee": None, "status": "assigned"},
        "junk",
    ]
    mock_connection.api_call.return_value = rows
    assert [a["id"] for a in approval_project_task.get_my_approvals(person_id=7)] == [1, 3]
    assert approval_project_task.get_my_approvals(person_id=99) == []


def test_get_my_approvals_ignores_a_bool_id(mock_connection, approval_project_task):
    mock_connection.api_call.return_value = [{"assignee": {"id": True}, "status": "approved"}]
    assert approval_project_task.get_my_approvals(person_id=1) == []


def test_get_my_approvals_without_a_known_user_raises(mock_connection, approval_project_task):
    mock_connection.api_user = None
    with pytest.raises(ValueError, match="person_id"):
        approval_project_task.get_my_approvals()
    mock_connection.api_call.assert_not_called()


def test_get_open_approvals_assigned_to_me(mock_connection):
    mock_connection.create_filter_string.return_value = "category=approval"
    mock_connection.api_call.return_value = [{"id": 5, "category": "approval"}]
    found = ProjectTask.get_open_approvals_assigned_to_me(mock_connection, max_results=20)
    mock_connection.create_filter_string.assert_called_once_with({"category": "approval"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/project_tasks/open_to_me?category=approval",
        "GET",
        max_results=20,
    )
    assert [t.id for t in found] == [5] and isinstance(found[0], ProjectTask)


def test_the_approval_statuses():
    assert [s.value for s in ProjectTaskApprovalStatus] == [
        "registered", "assigned", "rejected", "approved", "canceled",
    ]
    assert PROJECT_TASK_APPROVAL_PENDING == {"registered", "assigned"}
    assert str(ProjectTaskApprovalStatus.approved) == "approved"
    assert {s.value for s in ProjectTaskApprovalStatus} <= {
        s.value for s in ProjectTaskAssignmentStatus
    }
    assert str(ProjectTaskCategory.approval) == "approval"
