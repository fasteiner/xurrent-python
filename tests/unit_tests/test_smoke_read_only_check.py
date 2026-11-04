"""Unit tests for tests/smoke/read_only_check.py: the read-only guard and the output filter (no network)."""
import importlib.util
import io
import json
import os
import re
import sys
from unittest.mock import MagicMock, patch

import pytest
import requests
from requests.adapters import HTTPAdapter

HERE = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(HERE, "../../src")))

_spec = importlib.util.spec_from_file_location("read_only_check", os.path.join(HERE, "../smoke/read_only_check.py"))
roc = importlib.util.module_from_spec(_spec)
sys.modules["read_only_check"] = roc
_spec.loader.exec_module(roc)

import xurrent.core as xurrent_core  # noqa: E402
from xurrent.core import XurrentApiHelper  # noqa: E402
from xurrent.requests import Request  # noqa: E402

API = "https://api.example.com/v1"
TOKEN_URL = "https://oauth.example.com/token"


def make_policy(**kwargs):
    kwargs.setdefault("min_interval", 0)
    return roc.ReadOnlyPolicy(API, **kwargs)


def fake_response(request, payload=None, status=200, headers=None):
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps(payload).encode()
    response.headers.update({"Content-Type": "application/json; charset=utf-8", **(headers or {})})
    response.url = request.url
    response.request = request
    return response


# ---------------------------------------------------------------- policy

def test_policy_allows_get_to_api_host():
    make_policy().check("GET", f"{API}/requests?per_page=2")


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "post", "", None])
def test_policy_refuses_every_other_method(method):
    with pytest.raises(roc.ReadOnlyViolation):
        make_policy().check(method, f"{API}/requests")


@pytest.mark.parametrize("url", ["http://api.example.com/v1/requests", "https://evil.example.org/v1/requests",
                                 "https://oauth.example.com/token"])
def test_policy_refuses_get_to_other_hosts_and_plain_http(url):
    with pytest.raises(roc.ReadOnlyViolation):
        make_policy().check("GET", url)


def test_policy_refuses_get_with_body():
    with pytest.raises(roc.ReadOnlyViolation):
        make_policy().check("GET", f"{API}/requests", body=b'{"subject": "x"}')


def test_policy_allows_the_token_request_only_with_client_credentials():
    body = "client_id=a&client_secret=b&grant_type=client_credentials"
    with pytest.raises(roc.ReadOnlyViolation):
        make_policy().check("POST", TOKEN_URL, body)
    policy = make_policy(allow_token_request=True)
    policy.check("POST", TOKEN_URL, body)
    policy.check("POST", TOKEN_URL, {"grant_type": "client_credentials"})
    for url, data in [(f"{API}/requests", body), ("https://oauth.example.com/other", body),
                      (TOKEN_URL, "grant_type=password"), (TOKEN_URL, None),
                      ("https://oauth.evil.org/token", body)]:
        with pytest.raises(roc.ReadOnlyViolation):
            policy.check("POST", url, data)


def test_policy_budget_counts_requests_and_time():
    now = [0.0]
    policy = make_policy(max_requests=2, max_seconds=10, clock=lambda: now[0])
    policy.charge()
    policy.charge()
    with pytest.raises(roc.BudgetExceeded):
        policy.charge()
    policy = make_policy(max_requests=100, max_seconds=10, clock=lambda: now[0])
    now[0] = 10.0
    with pytest.raises(roc.BudgetExceeded):
        policy.charge()


def test_policy_keeps_the_interval_between_requests():
    now = [0.0]
    sleeps = []
    policy = roc.ReadOnlyPolicy(API, min_interval=0.5, clock=lambda: now[0], sleep=sleeps.append)
    policy.charge()
    now[0] = 0.2
    policy.charge()
    assert sleeps == [pytest.approx(0.3)]


@pytest.mark.parametrize("url, expected", [
    (f"{API}/requests?per_page=100", f"{API}/requests?per_page=3"),
    (f"{API}/requests?q=a&per_page=2", f"{API}/requests?q=a&per_page=2"),
    (f"{API}/requests?per_page=0&x=1", f"{API}/requests?per_page=1&x=1"),
    (f"{API}/requests?per_page=abc", f"{API}/requests?per_page=3"),
    (f"{API}/requests/5", f"{API}/requests/5"),
])
def test_clamp_url_caps_per_page(url, expected):
    assert roc.ReadOnlyPolicy.clamp_url(url) == expected


# ---------------------------------------------------------------- helper (layer 1)

@pytest.mark.parametrize("method", ["POST", "PATCH", "PUT", "DELETE", "post"])
def test_api_call_refuses_non_get_before_sending(method):
    helper = roc.ReadOnlyXurrentApiHelper(API, "key", "account", False)
    with patch.object(HTTPAdapter, "send") as send, patch("requests.request") as plain_request:
        with pytest.raises(roc.ReadOnlyViolation):
            helper.api_call(f"{API}/requests", method, {"subject": "x"})
    send.assert_not_called()
    plain_request.assert_not_called()


def test_domain_write_methods_are_refused_before_sending():
    helper = roc.ReadOnlyXurrentApiHelper(API, "key", "account", False)
    with patch.object(HTTPAdapter, "send") as send, patch("requests.request") as plain_request:
        with pytest.raises(roc.ReadOnlyViolation):
            Request.create(helper, {"subject": "x"})
        with pytest.raises(roc.ReadOnlyViolation):
            Request(helper, id=1).update({"subject": "x"})
        with pytest.raises(roc.ReadOnlyViolation):
            Request(helper, id=1).add_note("x")
        with pytest.raises(roc.ReadOnlyViolation):
            helper.bulk_export("people")
    send.assert_not_called()
    plain_request.assert_not_called()


def test_api_call_caps_per_page_and_max_results():
    helper = roc.ReadOnlyXurrentApiHelper(API, "key", "account", False)
    with patch.object(XurrentApiHelper, "api_call", return_value=[]) as base_call:
        helper.api_call(f"{API}/requests", max_results=50)
        helper.api_call(f"{API}/people/me")
    assert base_call.call_args_list[0].args == (f"{API}/requests", "GET", None, 3, False, 3)
    assert base_call.call_args_list[1].args == (f"{API}/people/me", "GET", None, 3, False, None)


# ---------------------------------------------------------------- transport (layers 2 and 3)

def test_read_only_transport_swaps_and_restores_core_requests():
    original = xurrent_core.requests
    with roc.read_only_transport(make_policy()) as guarded:
        assert xurrent_core.requests is guarded
    assert xurrent_core.requests is original


def test_transport_refuses_non_get_even_if_api_call_is_not_guarded():
    helper = XurrentApiHelper(API, "key", "account", False)   # plain helper: no layer 1
    with patch.object(HTTPAdapter, "send") as send, patch("requests.request") as plain_request:
        with roc.read_only_transport(make_policy()):
            for method in ("POST", "PATCH", "DELETE"):
                with pytest.raises(roc.ReadOnlyViolation):
                    helper.api_call(f"{API}/requests/1", method, {"subject": "x"})
            with pytest.raises(roc.ReadOnlyViolation):
                xurrent_core.requests.put(f"{API}/requests/1", json={})
    send.assert_not_called()
    plain_request.assert_not_called()


def test_requests_stand_in_passes_on_only_exceptions_and_types():
    guarded = roc.ReadOnlyRequests(make_policy())
    assert guarded.exceptions is requests.exceptions
    for name in ("api", "sessions", "adapters", "patch_all"):
        with pytest.raises(AttributeError):
            getattr(guarded, name)
    assert isinstance(guarded.Session(), roc.ReadOnlySession)


def test_adapter_refuses_non_get_before_the_network():
    adapter = roc.ReadOnlyAdapter(make_policy())
    with patch.object(HTTPAdapter, "send") as send:
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            prepared = requests.Request(method, f"{API}/requests", json={"subject": "x"}).prepare()
            with pytest.raises(roc.ReadOnlyViolation):
                adapter.send(prepared)
    send.assert_not_called()


def test_adapter_caps_per_page_stops_pagination_and_sets_timeout():
    policy = make_policy(timeout=7)
    adapter = roc.ReadOnlyAdapter(policy)
    prepared = requests.Request("GET", f"{API}/requests?per_page=100").prepare()
    with patch.object(HTTPAdapter, "send", side_effect=lambda request, **kw: fake_response(
            request, {"id": 1, "subject": "x"}, headers={"Link": f'<{API}/requests?page=2>; rel="next"'})) as send:
        response = adapter.send(prepared, timeout=None)
    sent_request = send.call_args.args[0]
    assert sent_request.url.endswith("per_page=3")
    assert send.call_args.kwargs["timeout"] == 7
    assert "Link" not in response.headers
    assert policy.requests_sent == 1
    assert policy.last_keys == frozenset({"id", "subject"})


def test_adapter_aborts_on_long_retry_after():
    adapter = roc.ReadOnlyAdapter(make_policy())
    prepared = requests.Request("GET", f"{API}/requests").prepare()
    with patch.object(HTTPAdapter, "send", side_effect=lambda request, **kw: fake_response(
            request, [], status=429, headers={"Retry-After": "3600"})):
        with pytest.raises(roc.BudgetExceeded):
            adapter.send(prepared)


def test_oauth_token_request_is_the_only_post():
    sent = []

    def fake_send(request, **kwargs):
        sent.append((request.method, request.url))
        if request.url == TOKEN_URL:
            return fake_response(request, {"access_token": "t", "expires_in": 3600})
        return fake_response(request, [{"id": 1}])

    with patch.object(HTTPAdapter, "send", side_effect=fake_send):
        with roc.read_only_transport(make_policy(allow_token_request=True)):
            helper = roc.ReadOnlyXurrentApiHelper(API, api_account="account", resolve_user=False,
                                                  client_id="id", client_secret="secret")
            assert helper.api_call(f"{API}/requests") == [{"id": 1}]
        with roc.read_only_transport(make_policy(allow_token_request=False)):
            with pytest.raises(roc.ReadOnlyViolation):
                roc.ReadOnlyXurrentApiHelper(API, api_account="account", resolve_user=False,
                                             client_id="id", client_secret="secret")
    assert sent[0][0] == "POST" and sent[0][1] == TOKEN_URL
    assert [method for method, _ in sent[1:]] == ["GET"]


# ---------------------------------------------------------------- output filter

def make_reporter(**kwargs):
    out = io.StringIO()
    return roc.Reporter(out, **kwargs), out


def http_error(status, message):
    response = MagicMock()
    response.status_code = status
    return requests.exceptions.HTTPError(message, response=response)


def test_fail_line_has_type_and_status_but_never_the_message():
    reporter, out = make_reporter()
    reporter.fail("Request.get_by_id", http_error(404, "404 Client Error for url https://api/requests/987654 secret"))
    reporter.fail("Request.get_notes", ValueError("subject: Payroll of John Doe"))
    text = out.getvalue()
    assert "FAIL  Request.get_by_id  HTTPError  http=404" in text
    assert "FAIL  Request.get_notes  ValueError" in text
    for leaked in ("987654", "secret", "Payroll", "John", "https://"):
        assert leaked not in text


@pytest.mark.parametrize("value, shown", [
    ("waiting_for_customer", "waiting_for_customer"),
    ("in-progress", "in-progress"),
    ("Some free text", roc.REDACTED),
    ("john.doe@example.com", roc.REDACTED),
    ("123456", roc.REDACTED),
    ("a" * 60, roc.REDACTED),
    (None, roc.REDACTED),
    (17, roc.REDACTED),
])
def test_safe_code_shows_only_code_like_enum_values(value, shown):
    assert roc.safe_code(value) == shown


def test_safe_name_replaces_unexpected_characters():
    assert roc.safe_name("Request.get_requests[open]") == "Request.get_requests[open]"
    assert roc.safe_name("a b\nc'd\"e/f") == "a?b?c?d?e?f"
    assert len(roc.safe_name("x" * 500)) == 100


def test_reporter_prints_only_integers_as_counts():
    reporter, out = make_reporter()
    reporter.ok("Person.get_me", count="secret", fields=(1, "2", ["name", "secret value"]))
    text = out.getvalue()
    assert "secret " not in text and "n=" not in text
    assert "missing=name,secret?value" in text


def test_quiet_reporter_prints_only_failures():
    reporter, out = make_reporter(quiet=True)
    reporter.ok("A.get_as", count=2)
    reporter.skip("A.get_by_id", "no record")
    reporter.fail("B.get_bs", RuntimeError("x"))
    assert out.getvalue().splitlines() == ["FAIL  B.get_bs  RuntimeError"]


def test_summary_and_exit_codes():
    reporter, _ = make_reporter()
    reporter.ok("A.get_as", count=2)
    reporter.skip("A.get_by_id", "no record")
    assert reporter.exit_code() == 0
    summary = reporter.summary(requests_sent=3, seconds=1.5)
    assert "Summary: 2 checks: 1 ok, 0 failed, 1 skipped (no record: 1); 0 unknown enum values; 3 requests in 1 s" in summary
    assert reporter.exit_code("budget used up") == 2
    reporter.enum_value("Request.category", "brand_new")
    assert reporter.exit_code() == 1
    assert "Request.category = 'brand_new'  (1x)" in reporter.summary(3, 1)
    reporter.fail("B.get_bs", http_error(500, "boom"))
    assert reporter.exit_code() == 1
    assert "  B.get_bs  HTTPError  http=500" in reporter.summary(3, 1)


def test_runner_reports_exceptions_by_type_only():
    reporter, out = make_reporter()
    runner = roc.Runner(MagicMock(), reporter, make_policy())

    def boom():
        raise ValueError("Confidential subject 42")

    assert runner.run("Request.get_requests", boom) is None
    assert out.getvalue().strip() == "FAIL  Request.get_requests  ValueError"


def test_runner_does_not_swallow_budget_exceeded():
    runner = roc.Runner(MagicMock(), make_reporter()[0], make_policy())

    def over_budget():
        raise roc.BudgetExceeded("time budget used up")

    with pytest.raises(roc.BudgetExceeded):
        runner.run("X.get_xs", over_budget)


def test_runner_reports_missing_expected_fields_by_name_from_code():
    reporter, out = make_reporter()
    policy = make_policy()
    runner = roc.Runner(MagicMock(), reporter, policy)

    def fetch():
        policy.last_keys = frozenset({"id", "subject", "secret_api_only_field"})
        return Request(MagicMock(), id=1, subject="Secret subject")

    runner.run("Request.get_by_id", fetch, expected=["id", "subject", "status"])
    text = out.getvalue()
    assert "fields=2/3 missing=status" in text
    assert "secret" not in text.lower()


def test_unknown_enum_values_name_the_field():
    connection = MagicMock()
    assert roc.unknown_enum_values(Request(connection, id=1, category="incident", status="assigned")) == []
    found = roc.unknown_enum_values([Request(connection, id=1, category="brand_new", status="mystery")])
    assert ("Request.category", "brand_new", "enum_or_raw") in found
    assert ("Request.status", "mystery", "annotation") in found


def test_runner_records_unknown_enum_values():
    reporter, _ = make_reporter()
    runner = roc.Runner(MagicMock(), reporter, make_policy())
    runner.run("Request.get_requests", lambda: [Request(MagicMock(), id=1, category="brand_new")])
    assert reporter.enum_findings == {("Request.category", "brand_new"): 1}


# ---------------------------------------------------------------- whole run against a fake API

def test_full_run_sends_only_capped_gets_and_prints_no_content():
    sent = []

    def fake_api(request, **kwargs):
        sent.append((request.method, request.url))
        path = request.url.split("?")[0]
        record = {"id": 987654, "subject": "SECRET-SUBJECT", "name": "SECRET-NAME"}
        if re.search(r"/(\d+|me)$", path):
            return fake_response(request, record)
        return fake_response(request, [record, dict(record, id=987655)],
                             headers={"Link": f'<{path}?page=2&per_page=2>; rel="next"'})

    out = io.StringIO()
    environ = {"APITOKEN": "TOKEN-VALUE", "APIACCOUNT": "ACCOUNT-VALUE", "APIURL": API}
    with patch.object(HTTPAdapter, "send", side_effect=fake_api):
        code = roc.main(["--min-interval", "0"], environ=environ, out=out)
    text = out.getvalue()

    assert code in (0, 1)
    assert sent and all(method == "GET" for method, _ in sent)
    assert not any(re.search(r"[?&]page=2", url) for _, url in sent)
    for _, url in sent:
        match = re.search(r"per_page=(\d+)", url)
        assert match is None or int(match.group(1)) <= roc.MAX_PAGE
    assert "Summary:" in text and "ABORTED" not in text
    for leaked in ("987654", "987655", "SECRET", "TOKEN-VALUE", "ACCOUNT-VALUE", "example.com"):
        assert leaked not in text
    # Every domain class was reached
    for name in ("Request.get_requests", "Request.get_by_id", "Request.get_notes[sort=-created_at]",
                 "Workflow.get_task_by_template_id", "Calendar.get_duration", "core.search[a]",
                 "core.list_audit_lines", "Person.get_me", "UiExtension.get_ui_extensions"):
        assert re.search(rf"^(ok|FAIL|skip) +{re.escape(name)}  ", text, re.MULTILINE), name


def test_missing_credentials_exit_with_2():
    out = io.StringIO()
    assert roc.main([], environ={}, out=out) == 2
    assert "Missing credentials" in out.getvalue()
