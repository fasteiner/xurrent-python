from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='TimeAllocation')


class TimeAllocationPredefinedFilter(str, Enum):
    enabled = "enabled"
    disabled = "disabled"

    def __str__(self):
        return self.value


class TimeAllocationCustomerCategory(str, Enum):
    none = "none"
    selected = "selected"
    any = "any"

    def __str__(self):
        return self.value


class TimeAllocationServiceCategory(str, Enum):
    none = "none"
    selected = "selected"
    any = "any"

    def __str__(self):
        return self.value


class TimeAllocationDescriptionCategory(str, Enum):
    hidden = "hidden"
    optional = "optional"
    required = "required"

    def __str__(self):
        return self.value


class TimeAllocation(JsonSerializableDict):
    # https://developer.xurrent.com/v1/time_allocations/
    __resourceUrl__ = 'time_allocations'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 group: Optional[str] = None,
                 disabled: Optional[bool] = None,
                 customer_category=None,
                 service_category=None,
                 description_category=None,
                 effort_class=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.group = group
        self.disabled = disabled
        self.customer_category = TimeAllocationCustomerCategory(customer_category) if customer_category else None
        self.service_category = TimeAllocationServiceCategory(service_category) if service_category else None
        self.description_category = TimeAllocationDescriptionCategory(description_category) if description_category else None

        from .effort_classes import EffortClass
        self.effort_class = (effort_class if isinstance(effort_class, EffortClass)
                             else EffortClass.from_data(connection_object, effort_class) if effort_class else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"TimeAllocation(id={self.id}, name={self.name}, disabled={self.disabled})"

    def ref_str(self) -> str:
        return f"TimeAllocation(id={self.id}, name={self.name})"

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
    def get_time_allocations(cls, connection_object: XurrentApiHelper,
                             predefinedFilter: TimeAllocationPredefinedFilter = None,
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
        return TimeAllocation.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def enable(self) -> T:
        return self.update({'disabled': False})

    def disable(self) -> T:
        return self.update({'disabled': True})
