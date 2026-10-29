from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='ShopArticle')


class ShopArticlePredefinedFilter(str, Enum):
    enabled = "enabled"
    disabled = "disabled"
    on_offer = "on_offer"

    def __str__(self):
        return self.value


class ShopArticleRecurringPeriod(str, Enum):
    monthly = "monthly"
    yearly = "yearly"

    def __str__(self):
        return self.value


class ShopArticle(JsonSerializableDict):
    # https://developer.xurrent.com/v1/shop_articles/
    __resourceUrl__ = 'shop_articles'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 reference: Optional[str] = None,
                 disabled: Optional[bool] = None,
                 price=None,
                 recurring_period=None,
                 max_quantity: Optional[int] = None,
                 short_description: Optional[str] = None,
                 full_description: Optional[str] = None,
                 picture_uri: Optional[str] = None,
                 category=None,
                 product=None,
                 calendar=None,
                 fulfillment_template=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.reference = reference
        self.disabled = disabled
        self.price = price
        self.recurring_period = ShopArticleRecurringPeriod(recurring_period) if recurring_period else None
        self.max_quantity = max_quantity
        self.short_description = short_description
        self.full_description = full_description
        self.picture_uri = picture_uri

        from .shop_article_categories import ShopArticleCategory
        self.category = (category if isinstance(category, ShopArticleCategory)
                         else ShopArticleCategory.from_data(connection_object, category)
                         if isinstance(category, dict) else category)

        from .products import Product
        self.product = (product if isinstance(product, Product)
                        else Product.from_data(connection_object, product) if product else None)

        from .calendars import Calendar
        self.calendar = (calendar if isinstance(calendar, Calendar)
                         else Calendar.from_data(connection_object, calendar) if calendar else None)

        from .request_templates import RequestTemplate
        self.fulfillment_template = (fulfillment_template if isinstance(fulfillment_template, RequestTemplate)
                                     else RequestTemplate.from_data(connection_object, fulfillment_template)
                                     if fulfillment_template else None)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return (f"ShopArticle(id={self.id}, name={self.name}, reference={self.reference}, "
                f"disabled={self.disabled})")

    def ref_str(self) -> str:
        return f"ShopArticle(id={self.id}, name={self.name})"

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
    def get_shop_articles(cls, connection_object: XurrentApiHelper,
                          predefinedFilter: ShopArticlePredefinedFilter = None,
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
        return ShopArticle.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def enable(self) -> T:
        return self.update({'disabled': False})

    def disable(self) -> T:
        return self.update({'disabled': True})
