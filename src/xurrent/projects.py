from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='Project')


class ProjectPredefinedFilter(str, Enum):
    completed = "completed"
    open = "open"
    managed_by_me = "managed_by_me"

    def __str__(self):
        return self.value


class ProjectStatus(str, Enum):
    being_created = "being_created"
    registered = "registered"
    in_progress = "in_progress"
    progress_halted = "progress_halted"
    completed = "completed"

    def __str__(self):
        return self.value


class ProjectCategory(str, Enum):
    engineering = "engineering"
    implementation = "implementation"
    maintenance = "maintenance"
    migration = "migration"
    move = "move"
    other = "other"
    release = "release"

    def __str__(self):
        return self.value


class Project(JsonSerializableDict):
    # https://developer.xurrent.com/v1/projects/
    __resourceUrl__ = 'projects'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 subject: Optional[str] = None,
                 status: Optional[str] = None,
                 category: Optional[str] = None,
                 manager=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.subject = subject
        self.status = ProjectStatus(status) if isinstance(status, str) else status
        self.category = ProjectCategory(category) if isinstance(category, str) else category

        from .people import Person
        self.manager = (manager if isinstance(manager, Person)
                        else Person.from_data(connection_object, manager) if manager else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"Project(id={self.id}, subject={self.subject}, status={self.status}, "
                f"category={self.category})")

    def ref_str(self) -> str:
        return f"Project(id={self.id}, subject={self.subject})"

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
    def get_projects(cls, connection_object: XurrentApiHelper,
                     predefinedFilter: ProjectPredefinedFilter = None,
                     queryfilter: dict = None) -> List[T]:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        if predefinedFilter:
            uri = f'{uri}/{predefinedFilter}'
        if queryfilter:
            uri += '?' + connection_object.create_filter_string(queryfilter)
        response = connection_object.api_call(uri, 'GET')
        return [cls.from_data(connection_object, item) for item in response]

    def update(self, data: dict) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        return Project.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def archive(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/archive'
        response = self._connection_object.api_call(uri, 'POST')
        return Project.from_data(self._connection_object, response)

    def trash(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/trash'
        response = self._connection_object.api_call(uri, 'POST')
        return Project.from_data(self._connection_object, response)

    def restore(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/restore'
        response = self._connection_object.api_call(uri, 'POST')
        return Project.from_data(self._connection_object, response)

    def get_tasks(self, queryfilter: dict = None) -> List:
        from .tasks import Task
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/tasks'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Task.from_data(self._connection_object, item) for item in response]

    def get_phases(self, queryfilter: dict = None) -> List[dict]:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/phases'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        return self._connection_object.api_call(uri, 'GET')

    def get_workflows(self, queryfilter: dict = None) -> List:
        from .workflows import Workflow
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/workflows'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Workflow.from_data(self._connection_object, item) for item in response]

    def get_risks(self, queryfilter: dict = None) -> List[dict]:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/risks'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        return self._connection_object.api_call(uri, 'GET')

    def get_notes(self, queryfilter: dict = None) -> List[dict]:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/notes'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        return self._connection_object.api_call(uri, 'GET')

    def add_note(self, note) -> dict:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/notes'
        if isinstance(note, dict):
            return self._connection_object.api_call(uri, 'POST', note)
        elif isinstance(note, str):
            return self._connection_object.api_call(uri, 'POST', {'text': note})
