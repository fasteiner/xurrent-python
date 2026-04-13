from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='ShopArticleCategory')


class ShopArticleCategoryPredefinedFilter(str, Enum):
    directory = "directory"
    support_domain = "support_domain"

    def __str__(self):
        return self.value


class ShopArticleCategory(JsonSerializableDict):
    # https://developer.xurrent.com/v1/shop_article_categories/
    __resourceUrl__ = 'shop_article_categories'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 name: Optional[str] = None,
                 short_description: Optional[str] = None,
                 full_description: Optional[str] = None,
                 picture_uri: Optional[str] = None,
                 parent=None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.name = name
        self.short_description = short_description
        self.full_description = full_description
        self.picture_uri = picture_uri

        self.parent = (parent if isinstance(parent, ShopArticleCategory)
                       else ShopArticleCategory.from_data(connection_object, parent)
                       if isinstance(parent, dict) else parent)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"ShopArticleCategory(id={self.id}, name={self.name})"

    def ref_str(self) -> str:
        return f"ShopArticleCategory(id={self.id}, name={self.name})"

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
    def get_shop_article_categories(cls, connection_object: XurrentApiHelper,
                                    predefinedFilter: ShopArticleCategoryPredefinedFilter = None,
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
        return ShopArticleCategory.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)
