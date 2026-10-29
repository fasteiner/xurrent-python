from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='EffortClass')


class EffortClassPredefinedFilter(str, Enum):
    enabled = "enabled"
    disabled = "disabled"

    def __str__(self):
        return self.value


class EffortClass(JsonSerializableDict):
    # https://developer.xurrent.com/v1/effort_classes/
    __resourceUrl__ = 'effort_classes'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 cost_multiplier: Optional[float] = None,
                 position: Optional[int] = None,
                 disabled: Optional[bool] = None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.cost_multiplier = cost_multiplier
        self.position = position
        self.disabled = disabled
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"EffortClass(id={self.id}, name={self.name}, disabled={self.disabled})"

    def ref_str(self) -> str:
        return f"EffortClass(id={self.id}, name={self.name})"

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
    def get_effort_classes(cls, connection_object: XurrentApiHelper,
                           predefinedFilter: EffortClassPredefinedFilter = None,
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
        return EffortClass.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def enable(self) -> T:
        return self.update({'disabled': False})

    def disable(self) -> T:
        return self.update({'disabled': True})
