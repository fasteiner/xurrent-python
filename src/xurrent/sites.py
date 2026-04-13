from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='Site')


class SitePredefinedFilter(str, Enum):
    disabled = "disabled"
    enabled = "enabled"
    directory = "directory"
    support_domain = "support_domain"

    def __str__(self):
        return self.value


class Site(JsonSerializableDict):
    # https://developer.xurrent.com/v1/sites/
    __resourceUrl__ = 'sites'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 city: Optional[str] = None,
                 country: Optional[str] = None,
                 time_zone: Optional[str] = None,
                 disabled: Optional[bool] = None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.city = city
        self.country = country
        self.time_zone = time_zone
        self.disabled = disabled
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"Site(id={self.id}, name={self.name}, city={self.city}, country={self.country}, disabled={self.disabled})"

    def ref_str(self) -> str:
        return f"Site(id={self.id}, name={self.name})"

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
    def get_sites(cls, connection_object: XurrentApiHelper,
                  predefinedFilter: SitePredefinedFilter = None,
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
        return Site.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def enable(self) -> T:
        return self.update({'disabled': False})

    def disable(self, prefix: str = '', postfix: str = '') -> T:
        return self.update({'disabled': True, 'name': f'{prefix}{self.name}{postfix}'})

    def archive(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/archive'
        response = self._connection_object.api_call(uri, 'POST')
        return Site.from_data(self._connection_object, response)

    def trash(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/trash'
        response = self._connection_object.api_call(uri, 'POST')
        return Site.from_data(self._connection_object, response)

    def restore(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/restore'
        response = self._connection_object.api_call(uri, 'POST')
        return Site.from_data(self._connection_object, response)
