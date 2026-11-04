from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='OutOfOfficePeriod')


class OutOfOfficePeriodPredefinedFilter(str, Enum):
    open = "open"
    completed = "completed"

    def __str__(self):
        return self.value


class OutOfOfficePeriod(JsonSerializableDict):
    # https://developer.xurrent.com/v1/out_of_office_periods/
    __resourceUrl__ = 'out_of_office_periods'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 start_at=None,
                 end_at=None,
                 reason: Optional[str] = None,
                 person=None,
                 approval_delegate=None,
                 time_allocation=None,
                 effort_class=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.start_at = start_at
        self.end_at = end_at
        self.reason = reason

        from .people import Person
        self.person = (person if isinstance(person, Person)
                       else Person.from_data(connection_object, person) if person else None)
        self.approval_delegate = (approval_delegate if isinstance(approval_delegate, Person)
                                  else Person.from_data(connection_object, approval_delegate)
                                  if approval_delegate else None)

        from .time_allocations import TimeAllocation
        self.time_allocation = (time_allocation if isinstance(time_allocation, TimeAllocation)
                                else TimeAllocation.from_data(connection_object, time_allocation)
                                if time_allocation else None)

        from .effort_classes import EffortClass
        self.effort_class = (effort_class if isinstance(effort_class, EffortClass)
                             else EffortClass.from_data(connection_object, effort_class)
                             if effort_class else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"OutOfOfficePeriod(id={self.id}, "
                f"person={self.person.ref_str() if self.person else None}, "
                f"start_at={self.start_at}, end_at={self.end_at})")

    def ref_str(self) -> str:
        return f"OutOfOfficePeriod(id={self.id}, start_at={self.start_at}, end_at={self.end_at})"

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
    def get_out_of_office_periods(cls, connection_object: XurrentApiHelper,
                                  predefinedFilter: OutOfOfficePeriodPredefinedFilter = None,
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
        return OutOfOfficePeriod.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def delete(self) -> None:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}'
        self._connection_object.api_call(uri, 'DELETE')
