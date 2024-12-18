from .core import XurrentApiHelper, JsonSerializableDict
from typing import Optional, List, Dict, Type, TypeVar
from .people import Person

from enum import Enum

class TeamPredefinedFilter(str, Enum):
    disabled = "disabled"  # List all disabled teams
    enabled = "enabled"  # List all enabled teams

T = TypeVar('T', bound='Team')

class Team(JsonSerializableDict):
    #https://developer.xurrent.com/v1/teams/
    __resourceUrl__ = 'teams'

    def __init__(self, connection_object: XurrentApiHelper, id, name: str = None, description: str = None, **kwargs):
        self._connection_object = connection_object
        self.id = id
        self.name = name
        self.description = description
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        """
        Return a string representation of the object.
        """
        return f"Team(id={self.id}, name={self.name}, description={self.description})"

    def ref_str(self) -> str:
        """
        Return a string representation of the object.
        """
        return f"Team(id={self.id}, name={self.name})"

    @classmethod
    def from_data(cls, connection_object: XurrentApiHelper, data) -> T:
        if not isinstance(data, dict):
            raise TypeError(f"Expected 'data' to be a dictionary, got {type(data).__name__}")
        if 'id' not in data:
            raise ValueError("Data dictionary must contain an 'id' field.")
        return cls(connection_object, **data)

    @classmethod
    def get_by_id(cls, connection_object: XurrentApiHelper, id) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}/{id}'
        return cls.from_data(connection_object, connection_object.api_call(uri, 'GET'))

    @classmethod
    def get_teams(cls, connection_object: XurrentApiHelper, predefinedFilter: TeamPredefinedFilter = None, queryfilter: dict = None) -> List[T]:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        if predefinedFilter:
            uri = f'{uri}/{predefinedFilter}'
        if queryfilter:
            uri += '?' + connection_object.create_filter_string(queryfilter)
        response = connection_object.api_call(uri, 'GET')
        return [cls.from_data(connection_object, team) for team in response]
    
    def get_members(self) -> List[Person]:
        """
        Retrieve the members of the team.
        """
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/members'
        response = self._connection_object.api_call(uri, 'GET')
        return [Person.from_data(self._connection_object, person) for person in response]

    def update(self, data) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        return Team.from_data(self._connection_object,response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        """
        Create a new team object.

        :param connection_object: Xurrent Connection object
        :param data: Data dictionary (containing the data for the new team)
        """
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        return cls.from_data(connection_object, connection_object.api_call(uri, 'POST', data))

    def enable(self, new_name: str = None) -> T:
        """
        Enable the team.
        """
        return self.update({'disabled': False, 'name': new_name or self.name})

    def disable(self, prefix: str = '', postfix: str = '') -> T:
        """
        Disable the team.
        """
        return self.update({'disabled': True, 'name': f'{prefix}{self.name}{postfix}'})

    def archive(self) -> T:
        """
        Archive the team.
        """
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/archive'
        return self._connection_object.api_call(uri, 'POST')

    def restore(self) -> T:
        """
        Restore the team.
        """
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/restore'
        return self._connection_object.api_call(uri, 'POST')

    def trash(self) -> T:
        """
        Trash the team.
        """
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/trash'
        return self._connection_object.api_call(uri, 'POST')
