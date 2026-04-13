from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='ShopOrderLine')


class ShopOrderLinePredefinedFilter(str, Enum):
    open = "open"
    completed = "completed"
    canceled = "canceled"
    personal = "personal"

    def __str__(self):
        return self.value


class ShopOrderLineStatus(str, Enum):
    in_cart = "in_cart"
    workflow_pending = "workflow_pending"
    fulfillment_pending = "fulfillment_pending"
    completed = "completed"
    canceled = "canceled"

    def __str__(self):
        return self.value


class ShopOrderLineRecurringPeriod(str, Enum):
    monthly = "monthly"
    yearly = "yearly"

    def __str__(self):
        return self.value


class ShopOrderLine(JsonSerializableDict):
    # https://developer.xurrent.com/v1/shop_order_lines/
    __resourceUrl__ = 'shop_order_lines'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 quantity=None,
                 status=None,
                 ordered_at=None,
                 completed_at=None,
                 shop_article=None,
                 requested_for=None,
                 requested_by=None,
                 fulfillment_request=None,
                 fulfillment_task=None,
                 fulfillment_template=None,
                 order=None,
                 recurring_period=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.quantity = quantity
        self.status = ShopOrderLineStatus(status) if status else None
        self.ordered_at = ordered_at
        self.completed_at = completed_at
        self.recurring_period = ShopOrderLineRecurringPeriod(recurring_period) if recurring_period else None

        from .shop_articles import ShopArticle
        self.shop_article = (shop_article if isinstance(shop_article, ShopArticle)
                             else ShopArticle.from_data(connection_object, shop_article)
                             if shop_article else None)

        from .people import Person
        self.requested_for = (requested_for if isinstance(requested_for, Person)
                              else Person.from_data(connection_object, requested_for)
                              if requested_for else None)
        self.requested_by = (requested_by if isinstance(requested_by, Person)
                             else Person.from_data(connection_object, requested_by)
                             if requested_by else None)

        from .requests import Request
        self.fulfillment_request = (fulfillment_request if isinstance(fulfillment_request, Request)
                                    else Request.from_data(connection_object, fulfillment_request)
                                    if fulfillment_request else None)
        self.order = (order if isinstance(order, Request)
                      else Request.from_data(connection_object, order) if order else None)

        from .tasks import Task
        self.fulfillment_task = (fulfillment_task if isinstance(fulfillment_task, Task)
                                 else Task.from_data(connection_object, fulfillment_task)
                                 if fulfillment_task else None)

        from .request_templates import RequestTemplate
        self.fulfillment_template = (fulfillment_template if isinstance(fulfillment_template, RequestTemplate)
                                     else RequestTemplate.from_data(connection_object, fulfillment_template)
                                     if fulfillment_template else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"ShopOrderLine(id={self.id}, name={self.name}, status={self.status}, "
                f"quantity={self.quantity})")

    def ref_str(self) -> str:
        return f"ShopOrderLine(id={self.id}, name={self.name})"

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
    def get_shop_order_lines(cls, connection_object: XurrentApiHelper,
                             predefinedFilter: ShopOrderLinePredefinedFilter = None,
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
        return ShopOrderLine.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)
