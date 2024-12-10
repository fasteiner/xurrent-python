import pytest
import os
import sys
from dotenv import load_dotenv

# Add the `../src` directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Now you can import the module
from xurrent.core import XurrentApiHelper
from xurrent.people import Person

# FILE: src/xurrent/test_core.py

@pytest.fixture
def x_api_helper():
    # Retrieve environment variables
    # Load .env file only if the environment variables are not already set
    if not os.getenv("APITOKEN") or not os.getenv("APIACCOUNT") or not os.getenv("APIURL"):
        load_dotenv()
    api_token = os.getenv("APITOKEN")  # Fetches DEMO_API_TOKEN, returns None if not set
    api_account = os.getenv("APIACCOUNT")
    api_url = os.getenv("APIURL")

    # Check if the environment variables are properly set
    if not all([api_token, api_account, api_url]):
        raise EnvironmentError("One or more environment variables are missing.")
    helper = XurrentApiHelper(api_url, api_token, api_account, True)
    return helper

def test_api_helper_setup(x_api_helper):
    api_token = os.getenv("APITOKEN")  # Fetches DEMO_API_TOKEN, returns None if not set
    api_account = os.getenv("APIACCOUNT")
    api_url = os.getenv("APIURL")
    assert x_api_helper is not None
    assert x_api_helper.base_url == api_url
    assert x_api_helper.api_account == api_account

    #check if the api_user is an instance of Person and has an id, which is int
    assert isinstance(x_api_helper.api_user, Person)
    assert x_api_helper.api_user.id is not None
    assert isinstance(x_api_helper.api_user.id, int)
    
    