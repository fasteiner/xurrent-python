from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='Risk')


class RiskPredefinedFilter(str, Enum):
    open = "open"
    closed = "closed"

    def __str__(self):
        return self.value


class RiskStatus(str, Enum):
    attrition = "attrition"
    availability = "availability"
    budget = "budget"
    compliance = "compliance"
    environmental = "environmental"
    legal = "legal"
    operational = "operational"
    program = "program"
    security = "security"
    strategic = "strategic"
    technology = "technology"

    def __str__(self):
        return self.value


class RiskSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    very_high = "very_high"

    def __str__(self):
        return self.value


class Risk(JsonSerializableDict):
    # https://developer.xurrent.com/v1/risks/
    __resourceUrl__ = 'risks'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 subject: Optional[str] = None,
                 status: Optional[str] = None,
                 severity: Optional[str] = None,
                 manager=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.subject = subject
        self.status = RiskStatus(status) if isinstance(status, str) else status
        self.severity = RiskSeverity(severity) if isinstance(severity, str) else severity

        from .people import Person
        self.manager = (manager if isinstance(manager, Person)
                        else Person.from_data(connection_object, manager) if manager else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"Risk(id={self.id}, subject={self.subject}, status={self.status}, "
                f"severity={self.severity})")

    def ref_str(self) -> str:
        return f"Risk(id={self.id}, subject={self.subject})"

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
    def get_risks(cls, connection_object: XurrentApiHelper,
                  predefinedFilter: RiskPredefinedFilter = None,
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
        return Risk.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def archive(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/archive'
        response = self._connection_object.api_call(uri, 'POST')
        return Risk.from_data(self._connection_object, response)

    def trash(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/trash'
        response = self._connection_object.api_call(uri, 'POST')
        return Risk.from_data(self._connection_object, response)

    def restore(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/restore'
        response = self._connection_object.api_call(uri, 'POST')
        return Risk.from_data(self._connection_object, response)

    def get_organizations(self, queryfilter: dict = None) -> List:
        from .organizations import Organization
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/organizations'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Organization.from_data(self._connection_object, item) for item in response]

    def get_projects(self, queryfilter: dict = None) -> List:
        from .projects import Project
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/projects'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Project.from_data(self._connection_object, item) for item in response]

    def get_services(self, queryfilter: dict = None) -> List:
        from .services import Service
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/services'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Service.from_data(self._connection_object, item) for item in response]
