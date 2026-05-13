from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='RequestTemplate')


class RequestTemplatePredefinedFilter(str, Enum):
    disabled = "disabled"
    enabled = "enabled"

    def __str__(self):
        return self.value


class RequestTemplateCategory(str, Enum):
    incident = "incident"
    rfc = "rfc"
    rfi = "rfi"
    reservation = "reservation"
    complaint = "complaint"
    compliment = "compliment"
    other = "other"

    def __str__(self):
        return self.value


class RequestTemplateStatus(str, Enum):
    declined = "declined"
    assigned = "assigned"
    accepted = "accepted"
    in_progress = "in_progress"
    waiting_for = "waiting_for"
    waiting_for_customer = "waiting_for_customer"
    workflow_pending = "workflow_pending"
    completed = "completed"

    def __str__(self):
        return self.value


class RequestTemplateImpact(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    top = "top"

    def __str__(self):
        return self.value


class RequestTemplate(JsonSerializableDict):
    # https://developer.xurrent.com/v1/request_templates/
    __resourceUrl__ = 'request_templates'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 subject: Optional[str] = None,
                 disabled: Optional[bool] = None,
                 category=None,
                 status=None,
                 impact=None,
                 service=None,
                 member=None,
                 team=None,
                 ci=None,
                 supplier=None,
                 workflow_template=None,
                 workflow_manager=None,
                 support_hours=None,
                 effort_class=None,
                 ui_extension=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.subject = subject
        self.disabled = disabled
        self.category = RequestTemplateCategory(category) if category else None
        self.status = RequestTemplateStatus(status) if status else None
        self.impact = RequestTemplateImpact(impact) if impact else None

        from .services import Service
        self.service = (service if isinstance(service, Service)
                        else Service.from_data(connection_object, service) if service else None)

        from .people import Person
        self.member = (member if isinstance(member, Person)
                       else Person.from_data(connection_object, member) if member else None)
        self.workflow_manager = (workflow_manager if isinstance(workflow_manager, Person)
                                 else Person.from_data(connection_object, workflow_manager)
                                 if workflow_manager else None)

        from .teams import Team
        self.team = (team if isinstance(team, Team)
                     else Team.from_data(connection_object, team) if team else None)

        from .configuration_items import ConfigurationItem
        self.ci = (ci if isinstance(ci, ConfigurationItem)
                   else ConfigurationItem.from_data(connection_object, ci) if ci else None)

        from .organizations import Organization
        self.supplier = (supplier if isinstance(supplier, Organization)
                         else Organization.from_data(connection_object, supplier) if supplier else None)

        from .workflow_templates import WorkflowTemplate
        self.workflow_template = (workflow_template if isinstance(workflow_template, WorkflowTemplate)
                                  else WorkflowTemplate.from_data(connection_object, workflow_template)
                                  if workflow_template else None)

        from .calendars import Calendar
        self.support_hours = (support_hours if isinstance(support_hours, Calendar)
                              else Calendar.from_data(connection_object, support_hours) if support_hours else None)

        from .effort_classes import EffortClass
        self.effort_class = (effort_class if isinstance(effort_class, EffortClass)
                             else EffortClass.from_data(connection_object, effort_class) if effort_class else None)

        from .ui_extensions import UiExtension
        self.ui_extension = (ui_extension if isinstance(ui_extension, UiExtension)
                             else UiExtension.from_data(connection_object, ui_extension)
                             if ui_extension else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"RequestTemplate(id={self.id}, subject={self.subject}, "
                f"category={self.category}, disabled={self.disabled})")

    def ref_str(self) -> str:
        return f"RequestTemplate(id={self.id}, subject={self.subject})"

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
    def get_request_templates(cls, connection_object: XurrentApiHelper,
                              predefinedFilter: RequestTemplatePredefinedFilter = None,
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
        return RequestTemplate.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def enable(self) -> T:
        return self.update({'disabled': False})

    def disable(self) -> T:
        return self.update({'disabled': True})
