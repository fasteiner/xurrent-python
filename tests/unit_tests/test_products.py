import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.products import Product, ProductPredefinedFilter, ProductDepreciationMethod
from xurrent.organizations import Organization
from xurrent.configuration_items import ConfigurationItem


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def product_instance(mock_connection):
    return Product(
        connection_object=mock_connection,
        id=10,
        name="Test Product",
        brand="Acme",
        model="X100",
        category="server",
        disabled=False,
        depreciation_method="straight_line",
        support_team=Team(connection_object=mock_connection, id=5, name="Support Team"),
    )


def test_product_initialization(product_instance):
    assert isinstance(product_instance, Product)
    assert product_instance.__resourceUrl__ == "products"
    assert product_instance.id == 10
    assert product_instance.name == "Test Product"
    assert product_instance.brand == "Acme"
    assert product_instance.model == "X100"
    assert product_instance.disabled is False
    assert product_instance.depreciation_method == ProductDepreciationMethod.straight_line
    assert isinstance(product_instance.support_team, Team)


def test_product_from_data(mock_connection):
    data = {
        "id": 10,
        "name": "Test Product",
        "brand": "Acme",
        "model": "X100",
        "category": "server",
        "disabled": False,
        "support_team": {"id": 5, "name": "Support Team"},
        "supplier": {"id": 20, "name": "Acme Corp"},
    }
    product = Product.from_data(mock_connection, data)
    assert isinstance(product, Product)
    assert product.id == 10
    assert isinstance(product.support_team, Team)
    assert isinstance(product.supplier, Organization)
    assert product.supplier.name == "Acme Corp"


def test_get_product_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 10, "name": "Test Product", "brand": "Acme", "model": "X100"}
    result = Product.get_by_id(mock_connection, 10)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/products/10", "GET"
    )
    assert isinstance(result, Product)
    assert result.id == 10


def test_get_products(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Product A", "brand": "BrandA", "model": "M1"},
        {"id": 2, "name": "Product B", "brand": "BrandB", "model": "M2"},
    ]
    results = Product.get_products(mock_connection)
    assert len(results) == 2
    assert all(isinstance(r, Product) for r in results)


def test_get_products_with_predefined_filter(mock_connection):
    mock_connection.api_call.return_value = []
    Product.get_products(mock_connection, predefinedFilter=ProductPredefinedFilter.enabled)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/products/enabled", "GET"
    )


def test_create_product(mock_connection):
    mock_connection.api_call.return_value = {"id": 11, "name": "New Product", "brand": "NewBrand", "model": "NM1"}
    result = Product.create(mock_connection, {"name": "New Product", "brand": "NewBrand", "model": "NM1"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/products", "POST",
        {"name": "New Product", "brand": "NewBrand", "model": "NM1"}
    )
    assert isinstance(result, Product)
    assert result.id == 11


def test_update_product(mock_connection, product_instance):
    mock_connection.api_call.return_value = {"id": 10, "name": "Updated Product", "brand": "Acme", "model": "X100"}
    result = product_instance.update({"name": "Updated Product"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/products/10", "PATCH", {"name": "Updated Product"}
    )
    assert isinstance(result, Product)
    assert result.name == "Updated Product"


def test_enable_product(mock_connection, product_instance):
    mock_connection.api_call.return_value = {"id": 10, "name": "Test Product", "brand": "Acme", "model": "X100", "disabled": False}
    product_instance.enable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/products/10", "PATCH", {"disabled": False}
    )


def test_disable_product(mock_connection, product_instance):
    mock_connection.api_call.return_value = {"id": 10, "name": "[DISABLED] Test Product", "brand": "Acme", "model": "X100", "disabled": True}
    product_instance.disable(prefix="[DISABLED] ")
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/products/10", "PATCH",
        {"disabled": True, "name": "[DISABLED] Test Product"}
    )


def test_get_cis(mock_connection, product_instance):
    mock_connection.api_call.return_value = [
        {"id": 100, "label": "CI-001", "name": "Server 1", "status": "active"},
    ]
    results = product_instance.get_cis()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/products/10/cis", "GET"
    )
    assert len(results) == 1
    assert isinstance(results[0], ConfigurationItem)


def test_depreciation_method_enum():
    assert str(ProductDepreciationMethod.straight_line) == "straight_line"
    assert str(ProductDepreciationMethod.not_depreciated) == "not_depreciated"
