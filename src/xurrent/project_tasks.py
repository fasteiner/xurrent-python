from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict, list_notes
from enum import Enum

T = TypeVar('T', bound='ProjectTask')


class ProjectTaskPredefinedFilter(str, Enum):
    finished = "finished"  # List all finished project tasks
    open = "open"  # List all open project tasks
    managed_by_me = "managed_by_me"  # List all project tasks of projects which manager is the API user
    assigned_to_me = "assigned_to_me"  # List all project tasks that are assigned to the API user
    open_to_me = "open_to_me"  # List all project tasks assigned to the API user with status Assigned, Accepted, In Progress or Waiting for

    def __str__(self):
        return self.value


class ProjectTaskStatus(str, Enum):
    registered = "registered"
    assigned = "assigned"
    accepted = "accepted"
    in_progress = "in_progress"
    waiting_for = "waiting_for"
    failed = "failed"
    rejected = "rejected"
    completed = "completed"
    approved = "approved"
    canceled = "canceled"

    def __str__(self):
        return self.value


class ProjectTaskAssignmentStatus(str, Enum):
    """The status of one assignment of a project task (GET /project_tasks/:id/assignments)."""
    registered = "registered"  # Registered
    assigned = "assigned"  # Assigned
    accepted = "accepted"  # Accepted
    in_progress = "in_progress"  # In Progress
    waiting_for = "waiting_for"  # Waiting for…
    failed = "failed"  # Failed
    rejected = "rejected"  # Rejected
    completed = "completed"  # Completed
    approved = "approved"  # Approved
    canceled = "canceled"  # Canceled

    def __str__(self):
        return self.value


class ProjectTaskApprovalStatus(str, Enum):
    """The status of one approval of a project task with category ``approval``: the statuses an
    approval task's approval has (registered, assigned, rejected, approved, canceled). Xurrent
    has no approvals collection for project tasks: each assignment of an approval project task
    is one approver's approval (see ``ProjectTask.get_approvals``)."""
    registered = "registered"  # Registered: the approval step has not started yet
    assigned = "assigned"  # Assigned: the approver is asked
    rejected = "rejected"  # Rejected
    approved = "approved"  # Approved
    canceled = "canceled"  # Canceled: counts for nothing

    def __str__(self):
        return self.value


# The approval statuses that still wait for the approver's decision.
PROJECT_TASK_APPROVAL_PENDING = frozenset({ProjectTaskApprovalStatus.registered.value,
                                           ProjectTaskApprovalStatus.assigned.value})


class ProjectTaskCategory(str, Enum):
    activity = "activity"
    approval = "approval"
    milestone = "milestone"

    def __str__(self):
        return self.value


class ProjectTask(JsonSerializableDict):
    """A task of a project, assigned to a team or a person."""
    # https://developer.xurrent.com/v1/project_tasks/
    __resourceUrl__ = 'project_tasks'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 subject: Optional[str] = None,
                 status: Optional[str] = None,
                 category: Optional[str] = None,
                 project=None,
                 manager=None,
                 team=None,
                 required_approvals: Optional[int] = None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.subject = subject
        # status and category stay plain strings, like Task, so unknown values from the API do not break parsing
        self.status = status
        self.category = category

        from .people import Person
        from .teams import Team
        self.manager = (manager if isinstance(manager, Person)
                        else Person.from_data(connection_object, manager) if manager else None)
        self.team = (team if isinstance(team, Team)
                     else Team.from_data(connection_object, team) if team else None)
        self.project = project
        # Approval project tasks: how many assignees must approve before the task is approved
        # (the API's default is 1; only the single-task read returns it).
        self.required_approvals = required_approvals

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"ProjectTask(id={self.id}, subject={self.subject}, status={self.status}, "
                f"category={self.category})")

    def ref_str(self) -> str:
        return f"ProjectTask(id={self.id}, subject={self.subject})"

    @classmethod
    def from_data(cls, connection_object: XurrentApiHelper, data) -> T:
        if not isinstance(data, dict):
            raise TypeError(f"Expected 'data' to be a dictionary, got {type(data).__name__}")
        if 'id' not in data:
            raise ValueError("Data dictionary must contain an 'id' field.")
        return cls(connection_object, **data)

    @classmethod
    def get_by_id(cls, connection_object: XurrentApiHelper, id: int) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}/{id}'
        return cls.from_data(connection_object, connection_object.api_call(uri, 'GET'))

    @classmethod
    def get_project_tasks(cls, connection_object: XurrentApiHelper,
                          predefinedFilter: ProjectTaskPredefinedFilter = None,
                          queryfilter: dict = None,
                          max_results: Optional[int] = None) -> List[T]:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        if predefinedFilter:
            uri = f'{uri}/{predefinedFilter}'
        if queryfilter:
            uri += '?' + connection_object.create_filter_string(queryfilter)
        if max_results:
            response = connection_object.api_call(uri, 'GET', max_results=max_results)
        else:
            response = connection_object.api_call(uri, 'GET')
        return [cls.from_data(connection_object, item) for item in response]

    @classmethod
    def get_open_approvals_assigned_to_me(cls, connection_object: XurrentApiHelper,
                                          max_results: Optional[int] = None) -> List[T]:
        """
        List the open project tasks with category ``approval`` assigned to the API user
        (GET /project_tasks/open_to_me?category=approval). The API has no ``approval_by_me``
        filter for project tasks as it has for tasks; an approval project task stays open
        until ``required_approvals`` assignees approved, so whether the API user's own approval
        still waits is in ``get_my_approvals()``.
        :param max_results: Return at most this many project tasks (default: all)
        :return: List of project tasks
        """
        return cls.get_project_tasks(connection_object,
                                     predefinedFilter=ProjectTaskPredefinedFilter.open_to_me,
                                     queryfilter={'category': ProjectTaskCategory.approval.value},
                                     max_results=max_results)

    def get_assignments(self, max_results: Optional[int] = None) -> List[dict]:
        """
        Retrieve the assignments of the current project task
        (GET /project_tasks/:id/assignments, all pages unless ``max_results``).
        Each assignment has its ``assignee`` (a person reference), its ``status``
        (``ProjectTaskAssignmentStatus``), ``planned_effort``, ``created_at`` and ``updated_at``.
        :param max_results: Return at most this many assignments (default: all)
        :return: List of assignments
        """
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/assignments'
        if max_results:
            response = self._connection_object.api_call(uri, 'GET', max_results=max_results)
        else:
            response = self._connection_object.api_call(uri, 'GET')
        return response if isinstance(response, list) else []

    def get_approvals(self, max_results: Optional[int] = None) -> List[dict]:
        """
        Retrieve the approvals of the current project task with category ``approval``, as
        ``Task.get_approvals`` does for an approval task. Xurrent has no approvals collection
        for project tasks: each assignment is one approver's approval, its ``assignee`` the
        approver and its ``status`` the decision (``ProjectTaskApprovalStatus``;
        ``PROJECT_TASK_APPROVAL_PENDING`` still waits). Unknown statuses are passed on as
        they are. Raises ``ValueError`` when the category is known and not ``approval``.
        :param max_results: Return at most this many approvals (default: all)
        :return: List of approvals (the assignments)
        """
        if self.category is not None and self.category != ProjectTaskCategory.approval:
            raise ValueError("Only approval project tasks have approvals.")
        return self.get_assignments(max_results=max_results)

    def get_my_approvals(self, person_id: Optional[int] = None) -> List[dict]:
        """
        Retrieve the approvals of the current approval project task that belong to one person:
        the API user (``connection_object.api_user``) unless ``person_id`` is given. Usually
        one; several when the person was assigned more than once. An empty list: the person is
        no approver. Raises ``ValueError`` when no ``person_id`` is given and the API user is
        not known (``XurrentApiHelper(resolve_user=False)``).
        :param person_id: The person's id (default: the API user's)
        :return: List of that person's approvals (assignments)
        """
        if person_id is None:
            api_user = getattr(self._connection_object, 'api_user', None)
            person_id = getattr(api_user, 'id', None)
            if person_id is None:
                raise ValueError("No person_id given and the API user is not known "
                                 "(XurrentApiHelper(resolve_user=False)).")
        mine = []
        for approval in self.get_approvals():
            assignee = approval.get('assignee') if isinstance(approval, dict) else None
            if isinstance(assignee, dict) and assignee.get('id') == person_id \
                    and not isinstance(assignee.get('id'), bool):
                mine.append(approval)
        return mine

    def update(self, data: dict) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        return ProjectTask.from_data(self._connection_object, response)

    @staticmethod
    def update_by_id(connection_object: XurrentApiHelper, id: int, data: dict) -> T:
        return ProjectTask(connection_object, id).update(data)

    def get_notes(self, queryfilter: dict = None, sort: Optional[str] = None,
                  max_results: Optional[int] = None) -> List[dict]:
        """
        Retrieve the notes of the current project task.
        :param queryfilter: Optional filter parameters (e.g. created_at, medium, person)
        :param sort: Optional order, e.g. '-created_at' for the newest note first (default: ascending by id)
        :param max_results: Return at most this many notes, fetching only the pages needed (default: all)
        :return: List of notes
        """
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/notes'
        return list_notes(self._connection_object, uri, queryfilter, sort, max_results)

    def add_note(self, note) -> dict:
        """
        Add a note to the current project task.
        :param note: Note text, or a dictionary with the note data (e.g. text, suppress_note_added_notifications)
        :return: The note that was added
        """
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/notes'
        if isinstance(note, dict):
            return self._connection_object.api_call(uri, 'POST', note)
        elif isinstance(note, str):
            return self._connection_object.api_call(uri, 'POST', {'text': note})
        else:
            raise TypeError(f"Expected 'note' to be a str or dict, got {type(note).__name__}")
