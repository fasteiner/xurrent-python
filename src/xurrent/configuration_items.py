from __future__ import annotations  # Needed for forward references
from .core import XurrentApiHelper, JsonSerializableDict
from typing import Optional, List, Dict, Type, TypeVar
from enum import Enum

T = TypeVar('T', bound='ConfigurationItem')

class ConfigurationItemPredefinedFilter(str, Enum):
    active = "active"  # List all active configuration items
    inactive = "inactive"  # List all inactive configuration items
    supported_by_my_teams = "supported_by_my_teams"  # List all configuration items supported by the teams of the API user

class ConfigurationItem(JsonSerializableDict):
    # https://developer.xurrent.com/v1/configuration_items/
    __resourceUrl__ = 'cis'

    def __init__(self, 
                 connection_object: XurrentApiHelper,
                 id: int,
                 label: Optional[str] = None,
                 name: Optional[str] = None,
                 type: Optional[str] = None,
                 status: Optional[str] = None,
                 attributes: Optional[Dict] = None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.label = label
        self.name = name
        self.status = status
        self.attributes = attributes or {}
        
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        """Provide a human-readable string representation of the object."""
        return f"ConfigurationItem(id={self.id}, label={self.label},name={self.name}, status={self.status})"

    def ref_str(self) -> str:
        """Provide a human-readable string representation of the object."""
        return f"ConfigurationItem(id={self.id}, label={self.label})"

    @classmethod
    def from_data(cls, connection_object: XurrentApiHelper, data) -> T:
        if not isinstance(data, dict):
            raise TypeError(f"Expected 'data' to be a dictionary, got {type(data).__name__}")
        if 'id' not in data:
            raise ValueError("Data dictionary must contain an 'id' field.")
        return cls(connection_object, **data)

    @classmethod
    def get_by_id(cls, connection_object: XurrentApiHelper, id: int) -> T:
        """
        Retrieve a configuration item by its ID.
        """
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}/{id}'
        return cls.from_data(connection_object, connection_object.api_call(uri, 'GET'))

    @classmethod
    def get_configuration_items(cls, connection_object: XurrentApiHelper, predefinedFilter: ConfigurationItemPredefinedFilter = None, queryfilter: dict = None) -> List[T]:
        """
        Retrieve all configuration items.
        """
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        if predefinedFilter:
            uri = f'{uri}/{predefinedFilter}'
        if queryfilter:
            uri += '?' + connection_object.create_filter_string(queryfilter)
        response = connection_object.api_call(uri, 'GET')
        return [cls.from_data(connection_object, ci) for ci in response]

    def update(self, data: dict) -> T:
        """
        Update the current configuration item instance with new data.
        """
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        return ConfigurationItem.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        """
        Create a new configuration item.
        """
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def archive(self) -> T:
        """
        Archive the configuration item.

        Allowed statuses for archiving:
        - undergoing_maintenance
        - broken_down
        - being_repaired
        - archived
        - to_be_removed
        - lost_or_stolen
        - removed
        """
        if self.status not in {"undergoing_maintenance", "broken_down", "being_repaired", "archived", "to_be_removed", "lost_or_stolen", "removed"}:
            raise ValueError("Configuration item must be in one of the following statuses to be archived: undergoing_maintenance, broken_down, being_repaired, archived, to_be_removed, lost_or_stolen, removed.")
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/archive'
        response = self._connection_object.api_call(uri, 'POST')
        return ConfigurationItem.from_data(self._connection_object, response)

    def restore(self) -> T:
        """
        Restore the configuration item.
        """
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/restore'
        response = self._connection_object.api_call(uri, 'POST')
        return ConfigurationItem.from_data(self._connection_object, response)

    def trash(self) -> T:
        """
        Trash the configuration item.

        Allowed statuses for trashing:
        - undergoing_maintenance
        - broken_down
        - being_repaired
        - archived
        - to_be_removed
        - lost_or_stolen
        - removed
        """
        if self.status not in {"undergoing_maintenance", "broken_down", "being_repaired", "archived", "to_be_removed", "lost_or_stolen", "removed"}:
            raise ValueError("Configuration item must be in one of the following statuses to be trashed: undergoing_maintenance, broken_down, being_repaired, archived, to_be_removed, lost_or_stolen, removed.")
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/trash'
        response = self._connection_object.api_call(uri, 'POST')
        return ConfigurationItem.from_data(self._connection_object, response)
