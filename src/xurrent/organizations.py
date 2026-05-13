from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='Organization')


class OrganizationPredefinedFilter(str, Enum):
    disabled = "disabled"
    enabled = "enabled"
    external = "external"
    internal = "internal"
    trusted = "trusted"
    directory = "directory"
    support_domain = "support_domain"
    managed_by_me = "managed_by_me"

    def __str__(self):
        return self.value


class Organization(JsonSerializableDict):
    # https://developer.xurrent.com/v1/organizations/
    __resourceUrl__ = 'organizations'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 disabled: Optional[bool] = None,
                 business_unit: Optional[bool] = None,
                 end_user_privacy: Optional[bool] = None,
                 parent=None,
                 business_unit_organization=None,
                 manager=None,
                 substitute=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.disabled = disabled
        self.business_unit = business_unit
        self.end_user_privacy = end_user_privacy

        self.parent = (parent if isinstance(parent, Organization)
                       else Organization.from_data(connection_object, parent) if parent else None)
        self.business_unit_organization = (
            business_unit_organization if isinstance(business_unit_organization, Organization)
            else Organization.from_data(connection_object, business_unit_organization)
            if business_unit_organization else None)

        from .people import Person
        self.manager = (manager if isinstance(manager, Person)
                        else Person.from_data(connection_object, manager) if manager else None)
        self.substitute = (substitute if isinstance(substitute, Person)
                           else Person.from_data(connection_object, substitute) if substitute else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"Organization(id={self.id}, name={self.name}, disabled={self.disabled}, "
                f"manager={self.manager.ref_str() if self.manager else None})")

    def ref_str(self) -> str:
        return f"Organization(id={self.id}, name={self.name})"

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
    def get_organizations(cls, connection_object: XurrentApiHelper,
                          predefinedFilter: OrganizationPredefinedFilter = None,
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
        return Organization.from_data(self._connection_object, response)

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
        return Organization.from_data(self._connection_object, response)

    def trash(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/trash'
        response = self._connection_object.api_call(uri, 'POST')
        return Organization.from_data(self._connection_object, response)

    def restore(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/restore'
        response = self._connection_object.api_call(uri, 'POST')
        return Organization.from_data(self._connection_object, response)

    def get_people(self, queryfilter: dict = None) -> List:
        from .people import Person
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/people'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Person.from_data(self._connection_object, p) for p in response]

    def get_children(self, queryfilter: dict = None) -> List[T]:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/child_organizations'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Organization.from_data(self._connection_object, item) for item in response]

    def get_addresses(self) -> List[dict]:
        """Retrieve addresses for this organization instance."""
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/addresses'
        return self._connection_object.api_call(uri, 'GET')

    def get_contacts(self) -> List[dict]:
        """Retrieve contacts for this organization instance."""
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/contacts'
        return self._connection_object.api_call(uri, 'GET')

    def get_contracts(self) -> List:
        """Retrieve contracts for this organization instance."""
        from .contracts import Contract
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/contracts'
        response = self._connection_object.api_call(uri, 'GET')
        return [Contract.from_data(self._connection_object, c) for c in response]

    def get_risks(self) -> List:
        """Retrieve risks for this organization instance."""
        from .risks import Risk
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/risks'
        response = self._connection_object.api_call(uri, 'GET')
        return [Risk.from_data(self._connection_object, r) for r in response]

    def get_slas(self) -> List[dict]:
        """Retrieve SLAs for this organization instance."""
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/slas'
        return self._connection_object.api_call(uri, 'GET')

    def get_time_allocations(self) -> List:
        """Retrieve time allocations for this organization instance."""
        from .time_allocations import TimeAllocation
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/time_allocations'
        response = self._connection_object.api_call(uri, 'GET')
        return [TimeAllocation.from_data(self._connection_object, ta) for ta in response]
