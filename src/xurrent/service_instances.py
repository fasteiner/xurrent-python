from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='ServiceInstance')


class ServiceInstancePredefinedFilter(str, Enum):
    active = "active"
    inactive = "inactive"

    def __str__(self):
        return self.value


class ServiceInstanceStatus(str, Enum):
    being_created = "being_created"
    active = "active"
    discontinued = "discontinued"

    def __str__(self):
        return self.value


class ServiceInstance(JsonSerializableDict):
    # https://developer.xurrent.com/v1/service_instances/
    __resourceUrl__ = 'service_instances'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 status: Optional[str] = None,
                 service=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.status = ServiceInstanceStatus(status) if isinstance(status, str) else status

        from .services import Service
        self.service = (service if isinstance(service, Service)
                        else Service.from_data(connection_object, service) if service else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"ServiceInstance(id={self.id}, name={self.name}, status={self.status})"

    def ref_str(self) -> str:
        return f"ServiceInstance(id={self.id}, name={self.name})"

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
    def get_service_instances(cls, connection_object: XurrentApiHelper,
                              predefinedFilter: ServiceInstancePredefinedFilter = None,
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
        return ServiceInstance.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def get_cis(self, queryfilter: dict = None) -> List:
        from .configuration_items import ConfigurationItem
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/cis'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [ConfigurationItem.from_data(self._connection_object, item) for item in response]

    def get_slas(self, queryfilter: dict = None) -> List[dict]:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/slas'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        return self._connection_object.api_call(uri, 'GET')

    def get_users(self, queryfilter: dict = None) -> List:
        from .people import Person
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/users'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Person.from_data(self._connection_object, item) for item in response]
