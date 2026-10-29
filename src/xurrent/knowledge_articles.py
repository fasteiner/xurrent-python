from __future__ import annotations
from typing import Optional, List, TypeVar
from .core import XurrentApiHelper, JsonSerializableDict
from enum import Enum

T = TypeVar('T', bound='KnowledgeArticle')


class KnowledgeArticlePredefinedFilter(str, Enum):
    active = "active"
    archived = "archived"
    managed_by_me = "managed_by_me"

    def __str__(self):
        return self.value


class KnowledgeArticleStatus(str, Enum):
    not_validated = "not_validated"
    validated = "validated"

    def __str__(self):
        return self.value


class KnowledgeArticle(JsonSerializableDict):
    # https://developer.xurrent.com/v1/knowledge_articles/
    __resourceUrl__ = 'knowledge_articles'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 subject: Optional[str] = None,
                 status: Optional[str] = None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.subject = subject
        self.status = KnowledgeArticleStatus(status) if isinstance(status, str) else status

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"KnowledgeArticle(id={self.id}, subject={self.subject}, status={self.status})"

    def ref_str(self) -> str:
        return f"KnowledgeArticle(id={self.id}, subject={self.subject})"

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
    def get_knowledge_articles(cls, connection_object: XurrentApiHelper,
                               predefinedFilter: KnowledgeArticlePredefinedFilter = None,
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
        return KnowledgeArticle.from_data(self._connection_object, response)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict) -> T:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def archive(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/archive'
        response = self._connection_object.api_call(uri, 'POST')
        return KnowledgeArticle.from_data(self._connection_object, response)

    def trash(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/trash'
        response = self._connection_object.api_call(uri, 'POST')
        return KnowledgeArticle.from_data(self._connection_object, response)

    def restore(self) -> T:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/restore'
        response = self._connection_object.api_call(uri, 'POST')
        return KnowledgeArticle.from_data(self._connection_object, response)

    def get_requests(self, queryfilter: dict = None) -> List:
        from .requests import Request
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/requests'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [Request.from_data(self._connection_object, item) for item in response]

    def get_service_instances(self, queryfilter: dict = None) -> List:
        from .service_instances import ServiceInstance
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/service_instances'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        response = self._connection_object.api_call(uri, 'GET')
        return [ServiceInstance.from_data(self._connection_object, item) for item in response]

    def get_translations(self, queryfilter: dict = None) -> List[dict]:
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/translations'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        return self._connection_object.api_call(uri, 'GET')
