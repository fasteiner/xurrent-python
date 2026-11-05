"""Shared fixture for the integration tests: a helper logged in to a live Xurrent account.

Credentials come from the environment, or from a ``.env`` file when none are set:

- OAuth client credentials (preferred): ``XURRENT_CLIENT_ID`` and ``XURRENT_CLIENT_SECRET``;
- or a personal API token: ``APITOKEN``;

plus the account and the API URL, as ``APIACCOUNT`` / ``APIURL`` (or ``XURRENT_ACCOUNT`` /
``XURRENT_API_URL``, the names the smoke check also reads).
"""

import os
import sys
from dataclasses import dataclass, field
from typing import Optional

import pytest
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from xurrent.core import XurrentApiHelper  # noqa: E402

OAUTH_KEYS = ("XURRENT_CLIENT_ID", "XURRENT_CLIENT_SECRET")


@dataclass
class IntegrationCredentials:
    api_url: str
    account: str
    api_key: Optional[str] = field(default=None, repr=False)
    client_id: Optional[str] = field(default=None, repr=False)
    client_secret: Optional[str] = field(default=None, repr=False)


def _first(*names: str) -> Optional[str]:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def load_integration_credentials() -> IntegrationCredentials:
    """The credentials of the environment (a ``.env`` file only fills in what is missing);
    OAuth wins when both a client and a token are set."""
    load_dotenv(override=False)
    api_url = _first("APIURL", "XURRENT_API_URL")
    account = _first("APIACCOUNT", "XURRENT_ACCOUNT")
    client_id, client_secret = (os.getenv(k) for k in OAUTH_KEYS)
    api_key = os.getenv("APITOKEN")
    if not api_url or not account:
        raise EnvironmentError("Set APIURL and APIACCOUNT (or XURRENT_API_URL and XURRENT_ACCOUNT).")
    if client_id and client_secret:
        return IntegrationCredentials(api_url, account, client_id=client_id, client_secret=client_secret)
    if api_key:
        return IntegrationCredentials(api_url, account, api_key=api_key)
    raise EnvironmentError(
        "Set XURRENT_CLIENT_ID and XURRENT_CLIENT_SECRET (OAuth) or APITOKEN (personal API token)."
    )


@pytest.fixture
def integration_credentials() -> IntegrationCredentials:
    return load_integration_credentials()


@pytest.fixture
def x_api_helper(integration_credentials: IntegrationCredentials) -> XurrentApiHelper:
    creds = integration_credentials
    return XurrentApiHelper(
        creds.api_url,
        api_key=creds.api_key,
        api_account=creds.account,
        resolve_user=True,
        client_id=creds.client_id,
        client_secret=creds.client_secret,
    )
