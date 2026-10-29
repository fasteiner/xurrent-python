from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='WorkflowTemplate')


class WorkflowTemplatePredefinedFilter(str, Enum):
    disabled = "disabled"
    enabled = "enabled"

    def __str__(self):
        return self.value


class WorkflowTemplateCategory(str, Enum):
    standard = "standard"
    non_standard = "non_standard"
    emergency = "emergency"
    order = "order"

    def __str__(self):
        return self.value


class WorkflowTemplate(JsonSerializableDict):
    # https://developer.xurrent.com/v1/workflow_templates/
    __resourceUrl__ = 'workflow_templates'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 subject: Optional[str] = None,
                 disabled: Optional[bool] = None,
                 category=None,
                 service=None,
                 workflow_manager=None,
                 ui_extension=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.subject = subject
        self.disabled = disabled
        self.category = WorkflowTemplateCategory(category) if category else None

        from .services import Service
        self.service = (service if isinstance(service, Service)
                        else Service.from_data(connection_object, service) if service else None)

        from .people import Person
        self.workflow_manager = (workflow_manager if isinstance(workflow_manager, Person)
                                 else Person.from_data(connection_object, workflow_manager)
                                 if workflow_manager else None)

        from .ui_extensions import UiExtension
        self.ui_extension = (ui_extension if isinstance(ui_extension, UiExtension)
                             else UiExtension.from_data(connection_object, ui_extension)
                             if ui_extension else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"WorkflowTemplate(id={self.id}, subject={self.subject}, "
                f"category={self.category}, disabled={self.disabled})")

    def ref_str(self) -> str:
        return f"WorkflowTemplate(id={self.id}, subject={self.subject})"

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
    def get_workflow_templates(cls, connection_object: XurrentApiHelper,
                               predefinedFilter: WorkflowTemplatePredefinedFilter = None,
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
        return WorkflowTemplate.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def enable(self) -> T:
        return self.update({'disabled': False})

    def disable(self) -> T:
        return self.update({'disabled': True})
