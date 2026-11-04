import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.custom_collections import CustomCollection, CustomCollectionPredefinedFilter
from xurrent.custom_collection_elements import CustomCollectionElement, CustomCollectionElementPredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def collection_instance(mock_connection):
    return CustomCollection(
        connection_object=mock_connection,
        id=70,
        name="Priority Levels",
        reference="priority_levels",
        disabled=False,
    )


@pytest.fixture
def element_instance(mock_connection):
    return CustomCollectionElement(
        connection_object=mock_connection,
        id=80,
        name="high",
        reference="high",
        disabled=False,
    )


# --- CustomCollection Tests ---

def test_collection_initialization(collection_instance):
    assert isinstance(collection_instance, CustomCollection)
    assert collection_instance.__resourceUrl__ == "custom_collections"
    assert collection_instance.id == 70
    assert collection_instance.name == "Priority Levels"
    assert collection_instance.reference == "priority_levels"


def test_collection_from_data(mock_connection):
    data = {"id": 70, "name": "Priority Levels", "reference": "priority_levels", "disabled": False}
    col = CustomCollection.from_data(mock_connection, data)
    assert isinstance(col, CustomCollection)
    assert col.reference == "priority_levels"


def test_get_collection_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 70, "name": "Priority Levels", "reference": "priority_levels"}
    result = CustomCollection.get_by_id(mock_connection, 70)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/custom_collections/70", "GET"
    )
    assert isinstance(result, CustomCollection)


def test_get_custom_collections(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Col A", "reference": "col_a"},
        {"id": 2, "name": "Col B", "reference": "col_b"},
    ]
    results = CustomCollection.get_custom_collections(mock_connection)
    assert len(results) == 2
    assert all(isinstance(r, CustomCollection) for r in results)


def test_get_collections_with_predefined_filter(mock_connection):
    mock_connection.api_call.return_value = []
    CustomCollection.get_custom_collections(mock_connection, predefinedFilter=CustomCollectionPredefinedFilter.enabled)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/custom_collections/enabled", "GET"
    )


def test_create_collection(mock_connection):
    mock_connection.api_call.return_value = {"id": 71, "name": "New Col", "reference": "new_col"}
    result = CustomCollection.create(mock_connection, {"name": "New Col"})
    assert isinstance(result, CustomCollection)
    assert result.id == 71


def test_enable_collection(mock_connection, collection_instance):
    mock_connection.api_call.return_value = {"id": 70, "name": "Priority Levels", "reference": "priority_levels", "disabled": False}
    collection_instance.enable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/custom_collections/70", "PATCH", {"disabled": False}
    )


def test_disable_collection(mock_connection, collection_instance):
    mock_connection.api_call.return_value = {"id": 70, "name": "Priority Levels", "reference": "priority_levels", "disabled": True}
    collection_instance.disable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/custom_collections/70", "PATCH", {"disabled": True}
    )


def test_get_elements(mock_connection, collection_instance):
    mock_connection.api_call.return_value = [
        {"id": 80, "name": "high", "reference": "high"},
        {"id": 81, "name": "low", "reference": "low"},
    ]
    results = collection_instance.get_elements()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/custom_collections/70/collection_elements", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, CustomCollectionElement) for r in results)


# --- CustomCollectionElement Tests ---

def test_element_initialization(element_instance):
    assert isinstance(element_instance, CustomCollectionElement)
    assert element_instance.__resourceUrl__ == "custom_collection_elements"
    assert element_instance.id == 80
    assert element_instance.name == "high"


def test_element_from_data(mock_connection):
    data = {
        "id": 80,
        "name": "high",
        "reference": "high",
        "disabled": False,
        "custom_collection": {"id": 70, "name": "Priority Levels", "reference": "priority_levels"},
    }
    element = CustomCollectionElement.from_data(mock_connection, data)
    assert isinstance(element, CustomCollectionElement)
    assert isinstance(element.custom_collection, CustomCollection)


def test_get_element_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 80, "name": "high", "reference": "high"}
    result = CustomCollectionElement.get_by_id(mock_connection, 80)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/custom_collection_elements/80", "GET"
    )
    assert isinstance(result, CustomCollectionElement)


def test_get_elements_list(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 80, "name": "high", "reference": "high"},
        {"id": 81, "name": "low", "reference": "low"},
    ]
    results = CustomCollectionElement.get_custom_collection_elements(mock_connection)
    assert len(results) == 2


def test_get_elements_with_predefined_filter(mock_connection):
    mock_connection.api_call.return_value = []
    CustomCollectionElement.get_custom_collection_elements(
        mock_connection, predefinedFilter=CustomCollectionElementPredefinedFilter.disabled
    )
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/custom_collection_elements/disabled", "GET"
    )


def test_create_element(mock_connection):
    mock_connection.api_call.return_value = {"id": 82, "name": "medium", "reference": "medium"}
    result = CustomCollectionElement.create(mock_connection, {"name": "medium"})
    assert isinstance(result, CustomCollectionElement)
    assert result.id == 82


def test_enable_element(mock_connection, element_instance):
    mock_connection.api_call.return_value = {"id": 80, "name": "high", "reference": "high", "disabled": False}
    element_instance.enable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/custom_collection_elements/80", "PATCH", {"disabled": False}
    )


def test_disable_element(mock_connection, element_instance):
    mock_connection.api_call.return_value = {"id": 80, "name": "high", "reference": "high", "disabled": True}
    element_instance.disable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/custom_collection_elements/80", "PATCH", {"disabled": True}
    )
