import os
import sys
from unittest.mock import MagicMock

import pytest
import requests

# Add the `../src` directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper


@pytest.fixture
def mock_token_response():
    def _factory(access_token="token", expires_in=3600):
        response = MagicMock()
        response.json.return_value = {"access_token": access_token, "expires_in": expires_in}
        response.raise_for_status = MagicMock()
        return response

    return _factory


def test_init_requires_authentication_method():
    with pytest.raises(ValueError):
        XurrentApiHelper("https://api.example.com", api_account="account", resolve_user=False)


def test_init_with_both_auth_methods_raises():
    with pytest.raises(ValueError):
        XurrentApiHelper(
            "https://api.example.com",
            api_key="token",
            api_account="account",
            resolve_user=False,
            client_id="cid",
            client_secret="secret",
        )


def test_client_credentials_fetches_token(monkeypatch, mock_token_response):
    post_calls = []

    def fake_post(url, data):
        post_calls.append((url, data))
        return mock_token_response("oauth-token")

    api_responses = []

    def fake_request(method, url, headers=None, json=None):
        api_responses.append({"method": method, "url": url, "headers": headers, "json": json})
        response = MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = {"result": "ok"}
        response.headers = {}
        return response

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(requests, "request", fake_request)

    helper = XurrentApiHelper(
        "https://api.example.com",
        api_account="account",
        resolve_user=False,
        client_id="cid",
        client_secret="secret",
    )

    result = helper.api_call("/resource")

    assert result == {"result": "ok"}
    assert post_calls == [
        (
            "https://oauth.xurrent.com/token",
            {
                "client_id": "cid",
                "client_secret": "secret",
                "grant_type": "client_credentials",
            },
        )
    ]
    assert api_responses[0]["headers"]["Authorization"] == "Bearer oauth-token"


def test_client_credentials_refreshes_token(monkeypatch):
    token_payloads = [
        {"access_token": "token-1", "expires_in": 0},
        {"access_token": "token-2", "expires_in": 3600},
    ]
    post_count = 0

    def fake_post(url, data):
        nonlocal post_count
        response = MagicMock()
        payload = token_payloads[post_count]
        response.json.return_value = payload
        response.raise_for_status = MagicMock()
        post_count += 1
        return response

    def fake_request(method, url, headers=None, json=None):
        response = MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = {"result": "ok"}
        response.headers = {}
        return response

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(requests, "request", fake_request)

    helper = XurrentApiHelper(
        "https://api.example.com",
        api_account="account",
        resolve_user=False,
        client_id="cid",
        client_secret="secret",
    )

    helper.api_call("/resource-1")
    helper.api_call("/resource-2")

    assert post_count == 2
