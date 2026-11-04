import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.services import Service, ServicePredefinedFilter
from xurrent.calendars import Calendar, CalendarPredefinedFilter
from xurrent.time_allocations import TimeAllocation, TimeAllocationPredefinedFilter, TimeAllocationCustomerCategory
from xurrent.effort_classes import EffortClass, EffortClassPredefinedFilter
from xurrent.request_templates import RequestTemplate, RequestTemplatePredefinedFilter, RequestTemplateCategory, RequestTemplateImpact
from xurrent.ui_extensions import UiExtension, UiExtensionCategory
from xurrent.workflow_templates import WorkflowTemplate, WorkflowTemplatePredefinedFilter, WorkflowTemplateCategory
from xurrent.organizations import Organization


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


# --- Service Tests ---

def test_service_initialization(mock_connection):
    svc = Service(
        connection_object=mock_connection,
        id=10,
        name="Email Service",
        disabled=False,
        provider=Organization(connection_object=mock_connection, id=20, name="IT Dept"),
    )
    assert isinstance(svc, Service)
    assert svc.__resourceUrl__ == "services"
    assert svc.id == 10
    assert isinstance(svc.provider, Organization)


def test_service_from_data(mock_connection):
    data = {
        "id": 10,
        "name": "Email Service",
        "disabled": False,
        "provider": {"id": 20, "name": "IT Dept"},
        "support_team": {"id": 5, "name": "IT Support"},
        "service_owner": {"id": 3, "name": "Alice"},
    }
    svc = Service.from_data(mock_connection, data)
    assert isinstance(svc, Service)
    assert isinstance(svc.provider, Organization)
    assert isinstance(svc.support_team, Team)
    assert isinstance(svc.service_owner, Person)


def test_get_service_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 10, "name": "Email Service"}
    result = Service.get_by_id(mock_connection, 10)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/services/10", "GET"
    )
    assert isinstance(result, Service)


def test_get_services(mock_connection):
    mock_connection.api_call.return_value = [{"id": 1, "name": "Svc A"}, {"id": 2, "name": "Svc B"}]
    results = Service.get_services(mock_connection)
    assert len(results) == 2
    assert all(isinstance(r, Service) for r in results)


def test_get_services_with_predefined_filter(mock_connection):
    mock_connection.api_call.return_value = []
    Service.get_services(mock_connection, predefinedFilter=ServicePredefinedFilter.enabled)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/services/enabled", "GET"
    )


def test_create_service(mock_connection):
    mock_connection.api_call.return_value = {"id": 11, "name": "New Service"}
    result = Service.create(mock_connection, {"name": "New Service", "provider_id": 20})
    assert isinstance(result, Service)
    assert result.id == 11


def test_enable_service(mock_connection):
    svc = Service(connection_object=mock_connection, id=10, name="Email Service", disabled=True)
    mock_connection.api_call.return_value = {"id": 10, "name": "Email Service", "disabled": False}
    svc.enable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/services/10", "PATCH", {"disabled": False}
    )


def test_disable_service(mock_connection):
    svc = Service(connection_object=mock_connection, id=10, name="Email Service", disabled=False)
    mock_connection.api_call.return_value = {"id": 10, "name": "[OLD] Email Service", "disabled": True}
    svc.disable(prefix="[OLD] ")
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/services/10", "PATCH",
        {"disabled": True, "name": "[OLD] Email Service"}
    )


# --- Calendar Tests ---

def test_calendar_initialization(mock_connection):
    cal = Calendar(connection_object=mock_connection, id=20, name="Business Hours", disabled=False)
    assert isinstance(cal, Calendar)
    assert cal.__resourceUrl__ == "calendars"
    assert cal.id == 20
    assert cal.name == "Business Hours"


def test_calendar_from_data(mock_connection):
    data = {"id": 20, "name": "Business Hours", "disabled": False}
    cal = Calendar.from_data(mock_connection, data)
    assert isinstance(cal, Calendar)


def test_get_calendar_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 20, "name": "Business Hours"}
    result = Calendar.get_by_id(mock_connection, 20)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/calendars/20", "GET"
    )
    assert isinstance(result, Calendar)


def test_get_calendars_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    Calendar.get_calendars(mock_connection, predefinedFilter=CalendarPredefinedFilter.enabled)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/calendars/enabled", "GET"
    )


def test_create_calendar(mock_connection):
    mock_connection.api_call.return_value = {"id": 21, "name": "After Hours"}
    result = Calendar.create(mock_connection, {"name": "After Hours"})
    assert isinstance(result, Calendar)


def test_enable_disable_calendar(mock_connection):
    cal = Calendar(connection_object=mock_connection, id=20, name="Business Hours", disabled=False)
    mock_connection.api_call.return_value = {"id": 20, "name": "Business Hours", "disabled": True}
    cal.disable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/calendars/20", "PATCH", {"disabled": True}
    )


# --- TimeAllocation Tests ---

def test_time_allocation_initialization(mock_connection):
    ta = TimeAllocation(
        connection_object=mock_connection,
        id=30,
        name="Internal Work",
        customer_category="none",
        service_category="any",
        description_category="optional",
    )
    assert isinstance(ta, TimeAllocation)
    assert ta.__resourceUrl__ == "time_allocations"
    assert ta.customer_category == TimeAllocationCustomerCategory.none


def test_time_allocation_from_data(mock_connection):
    data = {
        "id": 30,
        "name": "Internal Work",
        "customer_category": "selected",
        "service_category": "none",
        "description_category": "required",
        "effort_class": {"id": 5, "name": "Regular"},
    }
    ta = TimeAllocation.from_data(mock_connection, data)
    assert isinstance(ta, TimeAllocation)
    assert isinstance(ta.effort_class, EffortClass)


def test_get_time_allocations(mock_connection):
    mock_connection.api_call.return_value = [{"id": 1, "name": "TA A"}, {"id": 2, "name": "TA B"}]
    results = TimeAllocation.get_time_allocations(mock_connection)
    assert len(results) == 2


def test_get_time_allocations_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    TimeAllocation.get_time_allocations(mock_connection, predefinedFilter=TimeAllocationPredefinedFilter.disabled)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/time_allocations/disabled", "GET"
    )


# --- EffortClass Tests ---

def test_effort_class_initialization(mock_connection):
    ec = EffortClass(connection_object=mock_connection, id=5, name="Regular", cost_multiplier=1.0)
    assert isinstance(ec, EffortClass)
    assert ec.__resourceUrl__ == "effort_classes"
    assert ec.cost_multiplier == 1.0


def test_effort_class_from_data(mock_connection):
    data = {"id": 5, "name": "Regular", "cost_multiplier": 1.5, "position": 1, "disabled": False}
    ec = EffortClass.from_data(mock_connection, data)
    assert isinstance(ec, EffortClass)
    assert ec.cost_multiplier == 1.5


def test_get_effort_class_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 5, "name": "Regular"}
    result = EffortClass.get_by_id(mock_connection, 5)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/effort_classes/5", "GET"
    )
    assert isinstance(result, EffortClass)


def test_get_effort_classes_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    EffortClass.get_effort_classes(mock_connection, predefinedFilter=EffortClassPredefinedFilter.enabled)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/effort_classes/enabled", "GET"
    )


def test_create_effort_class(mock_connection):
    mock_connection.api_call.return_value = {"id": 6, "name": "Overtime"}
    result = EffortClass.create(mock_connection, {"name": "Overtime"})
    assert isinstance(result, EffortClass)


# --- RequestTemplate Tests ---

def test_request_template_initialization(mock_connection):
    rt = RequestTemplate(
        connection_object=mock_connection,
        id=40,
        subject="New Laptop Request",
        category="rfc",
        impact="medium",
        disabled=False,
    )
    assert isinstance(rt, RequestTemplate)
    assert rt.__resourceUrl__ == "request_templates"
    assert rt.category == RequestTemplateCategory.rfc
    assert rt.impact == RequestTemplateImpact.medium


def test_request_template_from_data(mock_connection):
    data = {
        "id": 40,
        "subject": "New Laptop Request",
        "category": "incident",
        "disabled": False,
        "service": {"id": 10, "name": "Email Service"},
        "team": {"id": 5, "name": "IT Support"},
        "member": {"id": 3, "name": "Alice"},
    }
    rt = RequestTemplate.from_data(mock_connection, data)
    assert isinstance(rt, RequestTemplate)
    assert isinstance(rt.service, Service)
    assert isinstance(rt.team, Team)
    assert isinstance(rt.member, Person)


def test_get_request_template_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 40, "subject": "New Laptop Request"}
    result = RequestTemplate.get_by_id(mock_connection, 40)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/request_templates/40", "GET"
    )
    assert isinstance(result, RequestTemplate)


def test_get_request_templates_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    RequestTemplate.get_request_templates(
        mock_connection, predefinedFilter=RequestTemplatePredefinedFilter.enabled
    )
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/request_templates/enabled", "GET"
    )


def test_enable_disable_request_template(mock_connection):
    rt = RequestTemplate(connection_object=mock_connection, id=40, subject="Req", disabled=True)
    mock_connection.api_call.return_value = {"id": 40, "subject": "Req", "disabled": False}
    rt.enable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/request_templates/40", "PATCH", {"disabled": False}
    )


# --- UiExtension Tests ---

def test_ui_extension_initialization(mock_connection):
    ue = UiExtension(
        connection_object=mock_connection,
        id=50,
        name="Custom Form",
        category="shop_article",
        disabled=False,
    )
    assert isinstance(ue, UiExtension)
    assert ue.__resourceUrl__ == "ui_extensions"
    assert ue.category == UiExtensionCategory.shop_article


def test_ui_extension_from_data(mock_connection):
    data = {
        "id": 50,
        "name": "Custom Form",
        "category": "product",
        "disabled": False,
        "created_by": {"id": 1, "name": "Admin"},
    }
    ue = UiExtension.from_data(mock_connection, data)
    assert isinstance(ue, UiExtension)
    assert ue.category == UiExtensionCategory.product
    assert isinstance(ue.created_by, Person)


def test_get_ui_extension_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 50, "name": "Custom Form", "category": "product"}
    result = UiExtension.get_by_id(mock_connection, 50)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/ui_extensions/50", "GET"
    )
    assert isinstance(result, UiExtension)


def test_get_ui_extensions(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 50, "name": "Form A", "category": "product"},
        {"id": 51, "name": "Form B", "category": "service"},
    ]
    results = UiExtension.get_ui_extensions(mock_connection)
    assert len(results) == 2


def test_enable_disable_ui_extension(mock_connection):
    ue = UiExtension(connection_object=mock_connection, id=50, name="Form", category="product", disabled=False)
    mock_connection.api_call.return_value = {"id": 50, "name": "Form", "category": "product", "disabled": True}
    ue.disable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/ui_extensions/50", "PATCH", {"disabled": True}
    )


# --- WorkflowTemplate Tests ---

def test_workflow_template_initialization(mock_connection):
    wt = WorkflowTemplate(
        connection_object=mock_connection,
        id=60,
        subject="Deploy New Release",
        category="standard",
        disabled=False,
    )
    assert isinstance(wt, WorkflowTemplate)
    assert wt.__resourceUrl__ == "workflow_templates"
    assert wt.category == WorkflowTemplateCategory.standard


def test_workflow_template_from_data(mock_connection):
    data = {
        "id": 60,
        "subject": "Deploy New Release",
        "category": "emergency",
        "disabled": False,
        "service": {"id": 10, "name": "Email Service"},
        "workflow_manager": {"id": 3, "name": "Alice"},
    }
    wt = WorkflowTemplate.from_data(mock_connection, data)
    assert isinstance(wt, WorkflowTemplate)
    assert wt.category == WorkflowTemplateCategory.emergency
    assert isinstance(wt.service, Service)
    assert isinstance(wt.workflow_manager, Person)


def test_get_workflow_template_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 60, "subject": "Deploy New Release", "category": "standard"}
    result = WorkflowTemplate.get_by_id(mock_connection, 60)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/workflow_templates/60", "GET"
    )
    assert isinstance(result, WorkflowTemplate)


def test_get_workflow_templates_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    WorkflowTemplate.get_workflow_templates(
        mock_connection, predefinedFilter=WorkflowTemplatePredefinedFilter.disabled
    )
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/workflow_templates/disabled", "GET"
    )


def test_create_workflow_template(mock_connection):
    mock_connection.api_call.return_value = {"id": 61, "subject": "New Template", "category": "standard"}
    result = WorkflowTemplate.create(mock_connection, {"subject": "New Template", "category": "standard"})
    assert isinstance(result, WorkflowTemplate)
    assert result.id == 61


def test_enable_workflow_template(mock_connection):
    wt = WorkflowTemplate(connection_object=mock_connection, id=60, subject="Deploy", category="standard", disabled=True)
    mock_connection.api_call.return_value = {"id": 60, "subject": "Deploy", "category": "standard", "disabled": False}
    wt.enable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/workflow_templates/60", "PATCH", {"disabled": False}
    )
