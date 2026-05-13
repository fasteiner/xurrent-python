from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict

T = TypeVar('T', bound='Holiday')


class Holiday(JsonSerializableDict):
    # https://developer.xurrent.com/v1/holidays/
    __resourceUrl__ = 'holidays'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 start_at=None,
                 end_at=None,
                 picture_uri: Optional[str] = None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.start_at = start_at
        self.end_at = end_at
        self.picture_uri = picture_uri
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"Holiday(id={self.id}, name={self.name}, start_at={self.start_at}, end_at={self.end_at})"

    def ref_str(self) -> str:
        return f"Holiday(id={self.id}, name={self.name})"

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
    def get_holidays(cls, connection_object: XurrentApiHelper,
                     queryfilter: dict = None) -> List[T]:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        if queryfilter:
            uri += '?' + connection_object.create_filter_string(queryfilter)
        response = connection_object.api_call(uri, 'GET')
        return [cls.from_data(connection_object, item) for item in response]

    def update(self, data: dict) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        return Holiday.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def get_calendars(self) -> List:
        """Retrieve calendars that contain this holiday."""
        from .calendars import Calendar
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/calendars'
        response = self._connection_object.api_call(uri, 'GET')
        return [Calendar.from_data(self._connection_object, c) for c in response]
