import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.knowledge_articles import KnowledgeArticle, KnowledgeArticlePredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def ka_instance(mock_connection):
    return KnowledgeArticle(
        connection_object=mock_connection,
        id=80,
        subject="How to reset password",
        status="validated",
    )


def test_knowledge_article_initialization(ka_instance):
    assert isinstance(ka_instance, KnowledgeArticle)
    assert ka_instance.__resourceUrl__ == "knowledge_articles"
    assert ka_instance.id == 80
    assert ka_instance.subject == "How to reset password"


def test_knowledge_article_from_data(mock_connection):
    data = {"id": 80, "subject": "How to reset password", "status": "validated"}
    ka = KnowledgeArticle.from_data(mock_connection, data)
    assert isinstance(ka, KnowledgeArticle)
    assert ka.id == 80


def test_get_knowledge_article_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 80, "subject": "How to reset password"}
    result = KnowledgeArticle.get_by_id(mock_connection, 80)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/knowledge_articles/80", "GET"
    )
    assert isinstance(result, KnowledgeArticle)
    assert result.id == 80


def test_get_knowledge_articles(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "subject": "KA A"},
        {"id": 2, "subject": "KA B"},
    ]
    results = KnowledgeArticle.get_knowledge_articles(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/knowledge_articles", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, KnowledgeArticle) for r in results)


def test_get_knowledge_articles_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    KnowledgeArticle.get_knowledge_articles(
        mock_connection, predefinedFilter=KnowledgeArticlePredefinedFilter.active
    )
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/knowledge_articles/active", "GET"
    )


def test_create_knowledge_article(mock_connection):
    mock_connection.api_call.return_value = {"id": 81, "subject": "New KA"}
    result = KnowledgeArticle.create(mock_connection, {"subject": "New KA"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/knowledge_articles", "POST", {"subject": "New KA"}
    )
    assert isinstance(result, KnowledgeArticle)
    assert result.id == 81


def test_update_knowledge_article(mock_connection, ka_instance):
    mock_connection.api_call.return_value = {"id": 80, "subject": "Updated KA"}
    result = ka_instance.update({"subject": "Updated KA"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/knowledge_articles/80", "PATCH", {"subject": "Updated KA"}
    )
    assert isinstance(result, KnowledgeArticle)
    assert result.subject == "Updated KA"


def test_archive_knowledge_article(mock_connection, ka_instance):
    mock_connection.api_call.return_value = {"id": 80, "subject": "How to reset password"}
    result = ka_instance.archive()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/knowledge_articles/80/archive", "POST"
    )
    assert isinstance(result, KnowledgeArticle)


def test_trash_knowledge_article(mock_connection, ka_instance):
    mock_connection.api_call.return_value = {"id": 80, "subject": "How to reset password"}
    result = ka_instance.trash()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/knowledge_articles/80/trash", "POST"
    )
    assert isinstance(result, KnowledgeArticle)


def test_restore_knowledge_article(mock_connection, ka_instance):
    mock_connection.api_call.return_value = {"id": 80, "subject": "How to reset password"}
    result = ka_instance.restore()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/knowledge_articles/80/restore", "POST"
    )
    assert isinstance(result, KnowledgeArticle)


def test_get_requests(mock_connection, ka_instance):
    from xurrent.requests import Request
    mock_connection.api_call.return_value = [{"id": 1, "subject": "Req A"}]
    results = ka_instance.get_requests()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/knowledge_articles/80/requests", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, Request) for r in results)


def test_get_service_instances(mock_connection, ka_instance):
    from xurrent.service_instances import ServiceInstance
    mock_connection.api_call.return_value = [{"id": 1, "name": "SI A"}]
    results = ka_instance.get_service_instances()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/knowledge_articles/80/service_instances", "GET"
    )
    assert len(results) == 1
    assert all(isinstance(r, ServiceInstance) for r in results)


def test_get_translations(mock_connection, ka_instance):
    translations_data = [{"id": 1, "language": "nl"}]
    mock_connection.api_call.return_value = translations_data
    result = ka_instance.get_translations()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/knowledge_articles/80/translations", "GET"
    )
    assert result == translations_data
