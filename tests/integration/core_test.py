import pytest
import os
import sys
import logging

# Add the `../src` directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# Now you can import the module
from xurrent.core import XurrentApiHelper
from xurrent.teams import Team
from xurrent.people import Person

# FILE: src/xurrent/test_core.py


def test_api_helper_setup(x_api_helper, integration_credentials):
    assert x_api_helper is not None
    assert x_api_helper.base_url == integration_credentials.api_url
    assert x_api_helper.api_account == integration_credentials.account

    #check if the api_user is an instance of Person and has an id, which is int
    assert isinstance(x_api_helper.api_user, Person)
    assert x_api_helper.api_user.id is not None
    assert isinstance(x_api_helper.api_user.id, int)

    #check if the api_user_teams is a list
    assert isinstance(x_api_helper.api_user_teams, list)
    for team in x_api_helper.api_user_teams:
        assert isinstance(team, Team)

    assert x_api_helper.logger.level == logging.INFO

def test_set_log_level(x_api_helper):
    x_api_helper.set_log_level("DEBUG")
    assert x_api_helper.logger.level == logging.DEBUG
    x_api_helper.set_log_level(logging.WARNING)
    assert x_api_helper.logger.level == logging.WARNING
    
    