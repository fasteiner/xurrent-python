from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='Service')


class ServicePredefinedFilter(str, Enum):
    disabled = "disabled"
    enabled = "enabled"

    def __str__(self):
        return self.value


class Service(JsonSerializableDict):
    # https://developer.xurrent.com/v1/services/
    __resourceUrl__ = 'services'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 disabled: Optional[bool] = None,
                 impact: Optional[str] = None,
                 keywords: Optional[str] = None,
                 provider=None,
                 support_team=None,
                 first_line_team=None,
                 service_owner=None,
                 availability_manager=None,
                 capacity_manager=None,
                 change_manager=None,
                 continuity_manager=None,
                 knowledge_manager=None,
                 problem_manager=None,
                 release_manager=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.disabled = disabled
        self.impact = impact
        self.keywords = keywords

        from .organizations import Organization
        self.provider = (provider if isinstance(provider, Organization)
                         else Organization.from_data(connection_object, provider) if provider else None)

        from .teams import Team
        self.support_team = (support_team if isinstance(support_team, Team)
                             else Team.from_data(connection_object, support_team) if support_team else None)
        self.first_line_team = (first_line_team if isinstance(first_line_team, Team)
                                else Team.from_data(connection_object, first_line_team) if first_line_team else None)

        from .people import Person
        self.service_owner = (service_owner if isinstance(service_owner, Person)
                              else Person.from_data(connection_object, service_owner) if service_owner else None)
        self.availability_manager = (availability_manager if isinstance(availability_manager, Person)
                                     else Person.from_data(connection_object, availability_manager)
                                     if availability_manager else None)
        self.capacity_manager = (capacity_manager if isinstance(capacity_manager, Person)
                                 else Person.from_data(connection_object, capacity_manager)
                                 if capacity_manager else None)
        self.change_manager = (change_manager if isinstance(change_manager, Person)
                               else Person.from_data(connection_object, change_manager) if change_manager else None)
        self.continuity_manager = (continuity_manager if isinstance(continuity_manager, Person)
                                   else Person.from_data(connection_object, continuity_manager)
                                   if continuity_manager else None)
        self.knowledge_manager = (knowledge_manager if isinstance(knowledge_manager, Person)
                                  else Person.from_data(connection_object, knowledge_manager)
                                  if knowledge_manager else None)
        self.problem_manager = (problem_manager if isinstance(problem_manager, Person)
                                else Person.from_data(connection_object, problem_manager)
                                if problem_manager else None)
        self.release_manager = (release_manager if isinstance(release_manager, Person)
                                else Person.from_data(connection_object, release_manager)
                                if release_manager else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"Service(id={self.id}, name={self.name}, disabled={self.disabled}, "
                f"provider={self.provider.ref_str() if self.provider else None})")

    def ref_str(self) -> str:
        return f"Service(id={self.id}, name={self.name})"

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
    def get_services(cls, connection_object: XurrentApiHelper,
                     predefinedFilter: ServicePredefinedFilter = None,
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
        return Service.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def enable(self) -> T:
        return self.update({'disabled': False})

    def disable(self, prefix: str = '', postfix: str = '') -> T:
        return self.update({'disabled': True, 'name': f'{prefix}{self.name}{postfix}'})

    def get_workflows(self, queryfilter: dict = None) -> List:
        """Retrieve workflows for this service instance."""
        from .workflows import Workflow
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/workflows'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Workflow.from_data(self._connection_object, w) for w in response]

    def get_request_templates(self) -> List:
        """Retrieve request templates for this service instance."""
        from .request_templates import RequestTemplate
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/request_templates'
        response = self._connection_object.api_call(uri, 'GET')
        return [RequestTemplate.from_data(self._connection_object, rt) for rt in response]

    def get_risks(self) -> List:
        """Retrieve risks for this service instance."""
        from .risks import Risk
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/risks'
        response = self._connection_object.api_call(uri, 'GET')
        return [Risk.from_data(self._connection_object, r) for r in response]

    def get_service_instances(self) -> List:
        """Retrieve service instances for this service."""
        from .service_instances import ServiceInstance
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/service_instances'
        response = self._connection_object.api_call(uri, 'GET')
        return [ServiceInstance.from_data(self._connection_object, si) for si in response]

    def get_slas(self) -> List[dict]:
        """Retrieve SLAs for this service instance."""
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/slas'
        return self._connection_object.api_call(uri, 'GET')

    def get_service_offerings(self) -> List:
        """Retrieve service offerings for this service."""
        from .service_offerings import ServiceOffering
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/service_offerings'
        response = self._connection_object.api_call(uri, 'GET')
        return [ServiceOffering.from_data(self._connection_object, so) for so in response]
