from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='CustomCollection')


class CustomCollectionPredefinedFilter(str, Enum):
    disabled = "disabled"
    enabled = "enabled"

    def __str__(self):
        return self.value


class CustomCollection(JsonSerializableDict):
    # https://developer.xurrent.com/v1/custom_collections/
    __resourceUrl__ = 'custom_collections'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 reference: Optional[str] = None,
                 disabled: Optional[bool] = None,
                 description: Optional[str] = None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.reference = reference
        self.disabled = disabled
        self.description = description
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"CustomCollection(id={self.id}, name={self.name}, reference={self.reference}, disabled={self.disabled})"

    def ref_str(self) -> str:
        return f"CustomCollection(id={self.id}, name={self.name})"

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
    def get_custom_collections(cls, connection_object: XurrentApiHelper,
                               predefinedFilter: CustomCollectionPredefinedFilter = None,
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
        return CustomCollection.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def enable(self) -> T:
        return self.update({'disabled': False})

    def disable(self) -> T:
        return self.update({'disabled': True})

    def get_elements(self, queryfilter: dict = None) -> List:
        from .custom_collection_elements import CustomCollectionElement
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/collection_elements'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [CustomCollectionElement.from_data(self._connection_object, item) for item in response]
