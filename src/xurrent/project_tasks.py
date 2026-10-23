from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
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


class ProjectTaskCategory(str, Enum):
    activity = "activity"
    approval = "approval"
    milestone = "milestone"

    def __str__(self):
        return self.value


class ProjectTask(JsonSerializableDict):
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

    def update(self, data: dict) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        return ProjectTask.from_data(self._connection_object, response)

    @staticmethod
    def update_by_id(connection_object: XurrentApiHelper, id: int, data: dict) -> T:
        return ProjectTask(connection_object, id).update(data)

    def get_notes(self, queryfilter: dict = None) -> List[dict]:
        """Retrieve all notes of the current project task."""
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/notes'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        return self._connection_object.api_call(uri, 'GET')

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
