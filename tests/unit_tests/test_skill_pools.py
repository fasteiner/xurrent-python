import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper
from xurrent.people import Person
from xurrent.teams import Team
from xurrent.skill_pools import SkillPool, SkillPoolPredefinedFilter


@pytest.fixture
def mock_connection():
    mock = MagicMock(spec=XurrentApiHelper)
    mock.base_url = "https://api.example.com"
    mock.api_user = Person(connection_object=mock, id=1, name="api_user")
    mock.api_user_teams = [Team(connection_object=mock, id=1, name="team")]
    return mock


@pytest.fixture
def sp_instance(mock_connection):
    return SkillPool(
        connection_object=mock_connection,
        id=110,
        name="Python Devs",
        disabled=False,
        manager=Person(connection_object=mock_connection, id=5, name="Manager"),
    )


def test_skill_pool_initialization(sp_instance):
    assert isinstance(sp_instance, SkillPool)
    assert sp_instance.__resourceUrl__ == "skill_pools"
    assert sp_instance.id == 110
    assert sp_instance.name == "Python Devs"
    assert sp_instance.disabled is False
    assert isinstance(sp_instance.manager, Person)


def test_skill_pool_from_data(mock_connection):
    data = {
        "id": 110,
        "name": "Python Devs",
        "disabled": False,
        "manager": {"id": 5, "name": "Manager"},
    }
    sp = SkillPool.from_data(mock_connection, data)
    assert isinstance(sp, SkillPool)
    assert sp.id == 110
    assert isinstance(sp.manager, Person)


def test_get_skill_pool_by_id(mock_connection):
    mock_connection.api_call.return_value = {"id": 110, "name": "Python Devs"}
    result = SkillPool.get_by_id(mock_connection, 110)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/skill_pools/110", "GET"
    )
    assert isinstance(result, SkillPool)
    assert result.id == 110


def test_get_skill_pools(mock_connection):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Pool A"},
        {"id": 2, "name": "Pool B"},
    ]
    results = SkillPool.get_skill_pools(mock_connection)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/skill_pools", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, SkillPool) for r in results)


def test_get_skill_pools_with_filter(mock_connection):
    mock_connection.api_call.return_value = []
    SkillPool.get_skill_pools(mock_connection, predefinedFilter=SkillPoolPredefinedFilter.enabled)
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/skill_pools/enabled", "GET"
    )


def test_create_skill_pool(mock_connection):
    mock_connection.api_call.return_value = {"id": 111, "name": "Java Devs"}
    result = SkillPool.create(mock_connection, {"name": "Java Devs"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/skill_pools", "POST", {"name": "Java Devs"}
    )
    assert isinstance(result, SkillPool)
    assert result.id == 111


def test_update_skill_pool(mock_connection, sp_instance):
    mock_connection.api_call.return_value = {"id": 110, "name": "Updated Pool"}
    result = sp_instance.update({"name": "Updated Pool"})
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/skill_pools/110", "PATCH", {"name": "Updated Pool"}
    )
    assert isinstance(result, SkillPool)
    assert result.name == "Updated Pool"


def test_enable_skill_pool(mock_connection, sp_instance):
    mock_connection.api_call.return_value = {"id": 110, "name": "Python Devs", "disabled": False}
    sp_instance.enable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/skill_pools/110", "PATCH", {"disabled": False}
    )


def test_disable_skill_pool(mock_connection, sp_instance):
    mock_connection.api_call.return_value = {"id": 110, "name": "Python Devs", "disabled": True}
    sp_instance.disable()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/skill_pools/110", "PATCH", {"disabled": True}
    )


def test_get_members(mock_connection, sp_instance):
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    results = sp_instance.get_members()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/skill_pools/110/members", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, Person) for r in results)


def test_get_effort_classes(mock_connection, sp_instance):
    from xurrent.effort_classes import EffortClass
    mock_connection.api_call.return_value = [
        {"id": 1, "name": "Regular"},
        {"id": 2, "name": "Overtime"},
    ]
    results = sp_instance.get_effort_classes()
    mock_connection.api_call.assert_called_once_with(
        f"{mock_connection.base_url}/skill_pools/110/effort_classes", "GET"
    )
    assert len(results) == 2
    assert all(isinstance(r, EffortClass) for r in results)
