from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='SkillPool')


class SkillPoolPredefinedFilter(str, Enum):
    disabled = "disabled"
    enabled = "enabled"

    def __str__(self):
        return self.value


class SkillPool(JsonSerializableDict):
    # https://developer.xurrent.com/v1/skill_pools/
    __resourceUrl__ = 'skill_pools'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 disabled: Optional[bool] = None,
                 manager=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.disabled = disabled

        from .people import Person
        self.manager = (manager if isinstance(manager, Person)
                        else Person.from_data(connection_object, manager) if manager else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"SkillPool(id={self.id}, name={self.name}, disabled={self.disabled})"

    def ref_str(self) -> str:
        return f"SkillPool(id={self.id}, name={self.name})"

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
    def get_skill_pools(cls, connection_object: XurrentApiHelper,
                        predefinedFilter: SkillPoolPredefinedFilter = None,
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
        return SkillPool.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def enable(self) -> T:
        return self.update({'disabled': False})

    def disable(self) -> T:
        return self.update({'disabled': True})

    def get_members(self, queryfilter: dict = None) -> List:
        from .people import Person
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/members'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Person.from_data(self._connection_object, item) for item in response]

    def get_effort_classes(self, queryfilter: dict = None) -> List:
        from .effort_classes import EffortClass
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/effort_classes'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [EffortClass.from_data(self._connection_object, item) for item in response]
