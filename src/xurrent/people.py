from .core import XurrentApiHelper
from typing import Optional, List, Dict, Type, TypeVar

from enum import Enum

class PeoplePredefinedFilter(str, Enum):
    disabled = "disabled"  # List all disabled people
    enabled = "enabled"  # List all enabled people
    internal = "internal"  # List all internal people
    directory = "directory"  # List all people registered in the directory account of the support domain account from which the data is requested
    support_domain = "support_domain"  # List all people registered in the account from which the data is requested (and not the related directory account)



T = TypeVar('T', bound='Person')

class Person():
    #https://developer.4me.com/v1/people/
    resourceUrl = 'people'

    def __init__(self, connection_object: XurrentApiHelper, id, name: str = None, primary_email: str = None,**kwargs):
        self._connection_object = connection_object
        self.id = id
        self.name = name
        self.primary_email = primary_email
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __update_object__(self, data) -> None:
        if data.get('id') != self.id:
            raise ValueError(f"ID mismatch: {self.id} != {data.get('id')}")
        for key, value in data.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        """
        Return a string representation of the object.
        """
        return f"Person(id={self.id}, name={self.name}, primary_email={self.primary_email})"

    @classmethod
    def from_data(cls, connection_object: XurrentApiHelper, data) -> T:
        if not isinstance(data, dict):
            raise TypeError(f"Expected 'data' to be a dictionary, got {type(data).__name__}")
        if 'id' not in data:
            raise ValueError("Data dictionary must contain an 'id' field.")
        return cls(connection_object, **data)

    @classmethod
    def get_by_id(cls, connection_object: XurrentApiHelper, id):
        uri = f'{connection_object.base_url}/{cls.resourceUrl}/{id}'
        return cls.from_data(connection_object, connection_object.api_call(uri, 'GET'))

    @classmethod
    def get_me(cls, connection_object: XurrentApiHelper):
        """
        Retrieve the person object for the authenticated user.
        """
        uri = f'{connection_object.base_url}/{cls.resourceUrl}/me'
        return cls.from_data(connection_object, connection_object.api_call(uri, 'GET'))

    @classmethod
    def get_people(cls, connection_object: XurrentApiHelper, predefinedFilter: PeoplePredefinedFilter = None, queryfilter: dict = None) -> List[T]:
        uri = f'{connection_object.base_url}/{cls.resourceUrl}'
        if predefinedFilter:
            uri = f'{uri}/{predefinedFilter}'
        if queryfilter:
            uri += '?' + connection_object.create_filter_string(queryfilter)
        response = connection_object.api_call(uri, 'GET')
        return [cls.from_data(connection_object, person) for person in response]
        
    def update(self, data):
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        self.__update_object__(response)
        return self
    
    def disable(self, prefix: str = '', postfix: str = ''):
        """
        Disable the person and update the name.

        :param prefix: Prefix to add to the name
        :param postfix: Postfix to add to the name
        :return: Updated person object
        """
        return self.update({
            'disabled': 'true',
            "name": f"{prefix}{self.name}{postfix}"
            })

    def enable(self):
        """
        Enable the person.
        """
        return self.update({
            'disabled': 'false'
        })

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict):
        """
        Create a new person object.

        :param connection_object: Xurrent Connection object
        :param data: Data dictionary (containing the data for the new person)
        """
        uri = f'{connection_object.base_url}/{cls.resourceUrl}'
        return cls.from_data(connection_object, connection_object.api_call(uri, 'POST', data))

    def archive(self):
        """
        Archive the person.
        """
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}/archive'
        return self._connection_object.api_call(uri, 'POST')
    
    def trash(self):
        """
        Trash the person.
        """
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}/trash'
        return self._connection_object.api_call(uri, 'POST')

    def restore(self):
        """
        Restore the person.
        """
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}/restore'
        return self._connection_object.api_call(uri, 'POST')

    