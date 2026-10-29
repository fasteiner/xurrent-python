from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='Product')


class ProductPredefinedFilter(str, Enum):
    disabled = "disabled"
    enabled = "enabled"
    supported_by_my_teams = "supported_by_my_teams"

    def __str__(self):
        return self.value


class ProductDepreciationMethod(str, Enum):
    not_depreciated = "not_depreciated"
    double_declining_balance = "double_declining_balance"
    reducing_balance = "reducing_balance"
    straight_line = "straight_line"
    sum_of_the_years_digits = "sum_of_the_years_digits"

    def __str__(self):
        return self.value


class Product(JsonSerializableDict):
    # https://developer.xurrent.com/v1/products/
    __resourceUrl__ = 'products'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 brand: Optional[str] = None,
                 model: Optional[str] = None,
                 category=None,
                 rule_set: Optional[str] = None,
                 disabled: Optional[bool] = None,
                 depreciation_method=None,
                 support_team=None,
                 supplier=None,
                 financial_owner=None,
                 workflow_manager=None,
                 service=None,
                 workflow_template=None,
                 ui_extension=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.brand = brand
        self.model = model
        self.rule_set = rule_set

        from .product_categories import ProductCategory
        self.category = (category if isinstance(category, ProductCategory)
                         else ProductCategory.from_data(connection_object, category)
                         if isinstance(category, dict) else category)
        self.disabled = disabled
        self.depreciation_method = ProductDepreciationMethod(depreciation_method) if depreciation_method else None

        from .teams import Team
        self.support_team = (support_team if isinstance(support_team, Team)
                             else Team.from_data(connection_object, support_team) if support_team else None)

        from .organizations import Organization
        self.supplier = (supplier if isinstance(supplier, Organization)
                         else Organization.from_data(connection_object, supplier) if supplier else None)
        self.financial_owner = (financial_owner if isinstance(financial_owner, Organization)
                                else Organization.from_data(connection_object, financial_owner)
                                if financial_owner else None)

        from .people import Person
        self.workflow_manager = (workflow_manager if isinstance(workflow_manager, Person)
                                 else Person.from_data(connection_object, workflow_manager)
                                 if workflow_manager else None)

        from .services import Service
        self.service = (service if isinstance(service, Service)
                        else Service.from_data(connection_object, service) if service else None)

        from .workflow_templates import WorkflowTemplate
        self.workflow_template = (workflow_template if isinstance(workflow_template, WorkflowTemplate)
                                  else WorkflowTemplate.from_data(connection_object, workflow_template)
                                  if workflow_template else None)

        from .ui_extensions import UiExtension
        self.ui_extension = (ui_extension if isinstance(ui_extension, UiExtension)
                             else UiExtension.from_data(connection_object, ui_extension)
                             if ui_extension else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"Product(id={self.id}, name={self.name}, brand={self.brand}, "
                f"model={self.model}, disabled={self.disabled})")

    def ref_str(self) -> str:
        return f"Product(id={self.id}, name={self.name})"

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
    def get_products(cls, connection_object: XurrentApiHelper,
                     predefinedFilter: ProductPredefinedFilter = None,
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
        return Product.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def enable(self) -> T:
        return self.update({'disabled': False})

    def disable(self, prefix: str = '', postfix: str = '') -> T:
        return self.update({'disabled': True, 'name': f'{prefix}{self.name}{postfix}'})

    def get_cis(self) -> List:
        from .configuration_items import ConfigurationItem
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/cis'
        response = self._connection_object.api_call(uri, 'GET')
        return [ConfigurationItem.from_data(self._connection_object, item) for item in response]
