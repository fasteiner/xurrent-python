import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.shop_article_categories import ShopArticleCategory, ShopArticleCategoryPredefinedFilter
from xurrent.shop_articles import ShopArticle, ShopArticlePredefinedFilter, ShopArticleRecurringPeriod
from xurrent.shop_order_lines import ShopOrderLine, ShopOrderLinePredefinedFilter, ShopOrderLineStatus


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def category_instance(mock_connection):
    return ShopArticleCategory(
        connection_object=mock_connection,
        id=90,
        name="Laptops",
        short_description="Laptop computers",
    )


@pytest.fixture
def article_instance(mock_connection, category_instance):
    return ShopArticle(
        connection_object=mock_connection,
        id=100,
        name="MacBook Pro",
        reference="MACBOOK-PRO",
        disabled=False,
        price=2499.00,
        recurring_period="monthly",
        max_quantity=1,
        category=category_instance,
    )


@pytest.fixture
def order_line_instance(mock_connection, article_instance):
    return ShopOrderLine(
        connection_object=mock_connection,
        id=200,
        name="Order #200",
        quantity=1,
        status="in_cart",
        shop_article=article_instance,
    )


# --- ShopArticleCategory Tests ---

def test_category_initialization(category_instance):
    assert isinstance(category_instance, ShopArticleCategory)
    assert category_instance.__resourceUrl__ == "shop_article_categories"
    assert category_instance.id == 90
    assert category_instance.name == "Laptops"


def test_category_from_data(mock_connection):
    data = {
        "id": 90,
        "name": "Laptops",
        "parent": {"id": 85, "name": "Hardware"},
    }
    cat = ShopArticleCategory.from_data(mock_connection, data)
    assert isinstance(cat, ShopArticleCategory)
    assert isinstance(cat.parent, ShopArticleCategory)
    assert cat.parent.name == "Hardware"


def test_get_category_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 90, "name": "Laptops"}
    result = ShopArticleCategory.get_by_id(mock_connection, 90)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/shop_article_categories/90", "GET"
    )
    assert isinstance(result, ShopArticleCategory)


def test_get_categories(mock_connection):
    mock_connection.api_call.return_value = [{"id": 1, "name": "Cat A"}, {"id": 2, "name": "Cat B"}]
    results = ShopArticleCategory.get_shop_article_categories(mock_connection)
    assert len(results) == 2
    assert all(isinstance(r, ShopArticleCategory) for r in results)


def test_get_categories_with_predefined_filter(mock_connection):
    mock_connection.api_call.return_value = []
    ShopArticleCategory.get_shop_article_categories(
        mock_connection, predefinedFilter=ShopArticleCategoryPredefinedFilter.directory
    )
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/shop_article_categories/directory", "GET"
    )


def test_create_category(mock_connection):
    mock_connection.api_call.return_value = {"id": 91, "name": "Monitors"}
    result = ShopArticleCategory.create(mock_connection, {"name": "Monitors"})
    assert isinstance(result, ShopArticleCategory)
    assert result.id == 91


def test_update_category(mock_connection, category_instance):
    mock_connection.api_call.return_value = {"id": 90, "name": "Laptops & Notebooks"}
    result = category_instance.update({"name": "Laptops & Notebooks"})
    assert isinstance(result, ShopArticleCategory)


# --- ShopArticle Tests ---

def test_article_initialization(article_instance):
    assert isinstance(article_instance, ShopArticle)
    assert article_instance.__resourceUrl__ == "shop_articles"
    assert article_instance.id == 100
    assert article_instance.name == "MacBook Pro"
    assert article_instance.recurring_period == ShopArticleRecurringPeriod.monthly
    assert isinstance(article_instance.category, ShopArticleCategory)


def test_article_from_data(mock_connection):
    data = {
        "id": 100,
        "name": "MacBook Pro",
        "reference": "MACBOOK-PRO",
        "disabled": False,
        "recurring_period": "yearly",
        "category": {"id": 90, "name": "Laptops"},
    }
    article = ShopArticle.from_data(mock_connection, data)
    assert isinstance(article, ShopArticle)
    assert article.recurring_period == ShopArticleRecurringPeriod.yearly
    assert isinstance(article.category, ShopArticleCategory)


def test_get_article_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 100, "name": "MacBook Pro", "reference": "MACBOOK-PRO"}
    result = ShopArticle.get_by_id(mock_connection, 100)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/shop_articles/100", "GET"
    )
    assert isinstance(result, ShopArticle)


def test_get_articles(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Item A", "reference": "ITEM-A"},
        {"id": 2, "name": "Item B", "reference": "ITEM-B"},
    ]
    results = ShopArticle.get_shop_articles(mock_connection)
    assert len(results) == 2
    assert all(isinstance(r, ShopArticle) for r in results)


def test_get_articles_with_predefined_filter(mock_connection):
    mock_connection.api_call.return_value = []
    ShopArticle.get_shop_articles(mock_connection, predefinedFilter=ShopArticlePredefinedFilter.on_offer)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/shop_articles/on_offer", "GET"
    )


def test_create_article(mock_connection):
    mock_connection.api_call.return_value = {"id": 101, "name": "New Article", "reference": "NEW-ART"}
    result = ShopArticle.create(mock_connection, {"name": "New Article", "reference": "NEW-ART"})
    assert isinstance(result, ShopArticle)
    assert result.id == 101


def test_enable_article(mock_connection, article_instance):
    mock_connection.api_call.return_value = {"id": 100, "name": "MacBook Pro", "reference": "MACBOOK-PRO", "disabled": False}
    article_instance.enable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/shop_articles/100", "PATCH", {"disabled": False}
    )


def test_disable_article(mock_connection, article_instance):
    mock_connection.api_call.return_value = {"id": 100, "name": "MacBook Pro", "reference": "MACBOOK-PRO", "disabled": True}
    article_instance.disable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/shop_articles/100", "PATCH", {"disabled": True}
    )


# --- ShopOrderLine Tests ---

def test_order_line_initialization(order_line_instance):
    assert isinstance(order_line_instance, ShopOrderLine)
    assert order_line_instance.__resourceUrl__ == "shop_order_lines"
    assert order_line_instance.id == 200
    assert order_line_instance.status == ShopOrderLineStatus.in_cart
    assert order_line_instance.quantity == 1
    assert isinstance(order_line_instance.shop_article, ShopArticle)


def test_order_line_from_data(mock_connection):
    data = {
        "id": 200,
        "name": "Order #200",
        "quantity": 2,
        "status": "fulfillment_pending",
        "shop_article": {"id": 100, "name": "MacBook Pro", "reference": "MACBOOK-PRO"},
        "requested_for": {"id": 5, "name": "Alice"},
    }
    line = ShopOrderLine.from_data(mock_connection, data)
    assert isinstance(line, ShopOrderLine)
    assert line.status == ShopOrderLineStatus.fulfillment_pending
    assert isinstance(line.shop_article, ShopArticle)
    assert isinstance(line.requested_for, Person)


def test_get_order_line_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 200, "name": "Order #200", "quantity": 1, "status": "in_cart"}
    result = ShopOrderLine.get_by_id(mock_connection, 200)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/shop_order_lines/200", "GET"
    )
    assert isinstance(result, ShopOrderLine)


def test_get_order_lines(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Line 1", "quantity": 1, "status": "in_cart"},
        {"id": 2, "name": "Line 2", "quantity": 2, "status": "completed"},
    ]
    results = ShopOrderLine.get_shop_order_lines(mock_connection)
    assert len(results) == 2
    assert all(isinstance(r, ShopOrderLine) for r in results)


def test_get_order_lines_with_predefined_filter(mock_connection):
    mock_connection.api_call.return_value = []
    ShopOrderLine.get_shop_order_lines(
        mock_connection, predefinedFilter=ShopOrderLinePredefinedFilter.personal
    )
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/shop_order_lines/personal", "GET"
    )


def test_create_order_line(mock_connection):
    mock_connection.api_call.return_value = {"id": 201, "name": "New Order", "quantity": 1, "status": "in_cart"}
    result = ShopOrderLine.create(mock_connection, {"shop_article_id": 100, "quantity": 1})
    assert isinstance(result, ShopOrderLine)
    assert result.id == 201


def test_update_order_line(mock_connection, order_line_instance):
    mock_connection.api_call.return_value = {"id": 200, "name": "Order #200", "quantity": 2, "status": "in_cart"}
    result = order_line_instance.update({"quantity": 2})
    assert isinstance(result, ShopOrderLine)


def test_order_line_status_enum():
    assert str(ShopOrderLineStatus.in_cart) == "in_cart"
    assert str(ShopOrderLineStatus.completed) == "completed"
    assert str(ShopOrderLineStatus.canceled) == "canceled"
