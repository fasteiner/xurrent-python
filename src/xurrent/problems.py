from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='Problem')


class ProblemPredefinedFilter(str, Enum):
    active = "active"
    known_errors = "known_errors"
    progress_halted = "progress_halted"
    solved = "solved"
    managed_by_me = "managed_by_me"
    assigned_to_my_teams = "assigned_to_my_teams"
    assigned_to_me = "assigned_to_me"

    def __str__(self):
        return self.value


class ProblemStatus(str, Enum):
    registered = "registered"
    in_progress = "in_progress"
    progress_halted = "progress_halted"
    solved = "solved"

    def __str__(self):
        return self.value


class ProblemImpact(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    top = "top"

    def __str__(self):
        return self.value


class Problem(JsonSerializableDict):
    # https://developer.xurrent.com/v1/problems/
    __resourceUrl__ = 'problems'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 subject: Optional[str] = None,
                 status: Optional[str] = None,
                 impact: Optional[str] = None,
                 manager=None,
                 team=None,
                 member=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.subject = subject
        self.status = ProblemStatus(status) if isinstance(status, str) else status
        self.impact = ProblemImpact(impact) if isinstance(impact, str) else impact

        from .people import Person
        self.manager = (manager if isinstance(manager, Person)
                        else Person.from_data(connection_object, manager) if manager else None)
        self.member = (member if isinstance(member, Person)
                       else Person.from_data(connection_object, member) if member else None)

        from .teams import Team
        self.team = (team if isinstance(team, Team)
                     else Team.from_data(connection_object, team) if team else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"Problem(id={self.id}, subject={self.subject}, status={self.status}, "
                f"impact={self.impact})")

    def ref_str(self) -> str:
        return f"Problem(id={self.id}, subject={self.subject})"

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
    def get_problems(cls, connection_object: XurrentApiHelper,
                     predefinedFilter: ProblemPredefinedFilter = None,
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
        return Problem.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def archive(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/archive'
        response = self._connection_object.api_call(uri, 'POST')
        return Problem.from_data(self._connection_object, response)

    def trash(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/trash'
        response = self._connection_object.api_call(uri, 'POST')
        return Problem.from_data(self._connection_object, response)

    def restore(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/restore'
        response = self._connection_object.api_call(uri, 'POST')
        return Problem.from_data(self._connection_object, response)

    def get_requests(self, queryfilter: dict = None) -> List:
        from .requests import Request
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/requests'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Request.from_data(self._connection_object, item) for item in response]

    def get_workflows(self, queryfilter: dict = None) -> List:
        from .workflows import Workflow
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/workflows'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Workflow.from_data(self._connection_object, item) for item in response]

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
