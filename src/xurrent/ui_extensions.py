from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='UiExtension')


class UiExtensionCategory(str, Enum):
    request_template = "request_template"
    knowledge_article_template = "knowledge_article_template"
    problem = "problem"
    release = "release"
    workflow_template = "workflow_template"
    task_template = "task_template"
    project = "project"
    project_task_template = "project_task_template"
    service = "service"
    service_instance = "service_instance"
    product = "product"
    product_category = "product_category"
    contract = "contract"
    organization = "organization"
    team = "team"
    person = "person"
    site = "site"
    risk = "risk"
    custom_collection = "custom_collection"
    scim_user = "scim_user"
    app_offering = "app_offering"
    shop_article = "shop_article"

    def __str__(self):
        return self.value


class UiExtension(JsonSerializableDict):
    # https://developer.xurrent.com/v1/ui_extensions/
    __resourceUrl__ = 'ui_extensions'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 category=None,
                 disabled: Optional[bool] = None,
                 title: Optional[str] = None,
                 created_by=None,
                 updated_by=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.category = UiExtensionCategory(category) if category else None
        self.disabled = disabled
        self.title = title

        from .people import Person
        self.created_by = (created_by if isinstance(created_by, Person)
                           else Person.from_data(connection_object, created_by) if created_by else None)
        self.updated_by = (updated_by if isinstance(updated_by, Person)
                           else Person.from_data(connection_object, updated_by) if updated_by else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"UiExtension(id={self.id}, name={self.name}, category={self.category}, disabled={self.disabled})"

    def ref_str(self) -> str:
        return f"UiExtension(id={self.id}, name={self.name})"

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
    def get_ui_extensions(cls, connection_object: XurrentApiHelper,
                          queryfilter: dict = None) -> List[T]:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        if queryfilter:
            uri += '?' + connection_object.create_filter_string(queryfilter)
        response = connection_object.api_call(uri, 'GET')
        return [cls.from_data(connection_object, item) for item in response]

    def update(self, data: dict) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        return UiExtension.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def enable(self) -> T:
        return self.update({'disabled': False})

    def disable(self) -> T:
        return self.update({'disabled': True})
