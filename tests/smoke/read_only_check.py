#!/usr/bin/env python3
"""
Read-only smoke check of the SDK against a real Xurrent account.

The unit tests only use mocks; this script calls the real API to see whether the domain classes and
helpers fit it. The checks are derived from the code, so new classes and methods are covered without
changes here. For every domain class in ``src/xurrent/``:

- every list function (a ``get_*`` classmethod without required arguments), unfiltered and with each
  value of its predefined filter enum, with ``max_results=2`` where supported;
- ``get_by_id`` on the first record found, and whether the fields the class expects (the named
  parameters of its ``__init__``) are in the response;
- every reading ``get_*`` sub-resource of that record (with each filter value, ``expand=True`` and
  ``get_notes(sort='-created_at', max_results=1)``), and the ``get_*`` class/static methods that only
  need the record's id;
- fields with an enum value the SDK does not know (kept as text by ``enum_or_raw``, or annotated with
  an enum but not converted).

Plus ``Person.get_me``, ``search('test', max_results=3)`` (the API answers queries of one character
with HTTP 400), ``list_archive``, ``list_trash`` and ``list_audit_lines``. A check whose record does
not exist in the account is skipped, not failed, and so are the KNOWN_SKIPS below (with their reason).
Values of account-defined enums (ACCOUNT_DEFINED_ENUMS) are listed for information only.

Safety, enforced in code:

- Only GET requests are sent. ``ReadOnlyXurrentApiHelper.api_call`` refuses every other method before
  anything is sent; a stand-in for the ``requests`` module inside ``xurrent.core`` and an HTTP adapter
  (the last step before the network) refuse them again. The single exception is the OAuth token
  request (POST to ``https://oauth.<domain>/token`` with the client credentials grant), and only when
  the check authenticates with client credentials.
- Requests go only to the API host over https (and to the OAuth host for the token).
- ``per_page`` and ``max_results`` are capped at 3, pagination stops after the first page, every request
  has a timeout, and the run has a request and time budget (default 800 requests, 300 seconds).

Output: only check names, ok/FAIL/skip, exception class, HTTP status, counts, missing expected fields
(names from the SDK code) and unknown enum values (field name and value, only if the value looks like
an API code). Never record contents, IDs or error message texts, which may quote response content.

Usage::

    python tests/smoke/read_only_check.py [--quiet] [--max-seconds 300] [--max-requests 800]

Credentials (environment, or a ``.env`` file if python-dotenv is installed):

- ``APITOKEN``, ``APIACCOUNT``, ``APIURL`` (API token, as in tests/integration), or
- ``XURRENT_CLIENT_ID``, ``XURRENT_CLIENT_SECRET``, ``XURRENT_ACCOUNT``, ``XURRENT_API_URL`` (OAuth).

Exit code: 0 when every check is ok or skipped, 1 when a check failed or an unknown enum value was
found, 2 when the run was aborted (missing credentials, failed login, budget used up).
"""
from __future__ import annotations

import argparse
import enum
import importlib
import inspect
import logging
import os
import pkgutil
import re
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, Iterator, List, Optional, Tuple
from urllib.parse import parse_qsl, urlsplit

import requests
from requests.adapters import HTTPAdapter

_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import xurrent  # noqa: E402
import xurrent.core as xurrent_core  # noqa: E402
from xurrent.core import JsonSerializableDict, XurrentApiHelper  # noqa: E402

MAX_PAGE = 3                 # upper limit for per_page and max_results
LIST_MAX_RESULTS = 2         # max_results for list functions and sub-resources
DEFAULT_MAX_REQUESTS = 800
DEFAULT_MAX_SECONDS = 300.0
DEFAULT_TIMEOUT = 20.0       # seconds per HTTP request
MIN_INTERVAL = 0.1           # seconds between two requests
MAX_RETRY_AFTER = 10         # longest Retry-After (seconds) the run waits for after HTTP 429

# Checks that are skipped on purpose: check name -> reason
KNOWN_SKIPS = {
    # The filter builds /problems/assigned_to_my_teams (404); kept for compatibility next to the
    # correct ProblemPredefinedFilter.assigned_to_my_team (see CHANGELOG)
    'Problem.get_problems[assigned_to_my_teams]': 'kept for compatibility, API answers 404',
}

# Enums whose values are references defined per account (e.g. GET /project_categories): other values
# are not SDK errors, so they are reported for information only
ACCOUNT_DEFINED_ENUMS = frozenset({'ProjectCategory', 'RiskSeverity'})


# --------------------------------------------------------------------------------------------------
# Read-only guard
# --------------------------------------------------------------------------------------------------

class ReadOnlyViolation(RuntimeError):
    """A request other than GET (or the OAuth token request) was about to be sent."""


class BudgetExceeded(RuntimeError):
    """The run used up its time or request budget, or the API asked to wait too long."""


def oauth_host(api_host: str) -> str:
    """Host of the OAuth token endpoint, derived like ``XurrentApiHelper._obtain_access_token``."""
    parts = api_host.split('.')
    parts[0] = 'oauth'
    return '.'.join(parts)


_PER_PAGE = re.compile(r'([?&])per_page=([^&#]*)')


class ReadOnlyPolicy:
    """What may be sent: GET to the API host over https, and, with client credentials, the OAuth
    token request. Also keeps the request and time budget and what the last GET returned."""

    def __init__(self, api_url: str, *, allow_token_request: bool = False,
                 max_requests: int = DEFAULT_MAX_REQUESTS, max_seconds: float = DEFAULT_MAX_SECONDS,
                 timeout: float = DEFAULT_TIMEOUT, min_interval: float = MIN_INTERVAL,
                 clock: Callable[[], float] = time.monotonic, sleep: Callable[[float], None] = time.sleep):
        host = (urlsplit(api_url).hostname or '').lower()
        if not host:
            raise ValueError('api_url must contain a host')
        self.api_host = host
        self.oauth_host = oauth_host(host)
        self.allow_token_request = allow_token_request
        self.max_requests = max_requests
        self.timeout = timeout
        self.min_interval = min_interval
        self._clock = clock
        self._sleep = sleep
        self.started = clock()
        self.deadline = self.started + max_seconds
        self.requests_sent = 0
        self._last_sent: Optional[float] = None
        self.last_status: Optional[int] = None
        self.last_keys: Optional[frozenset] = None

    def check(self, method, url, body=None) -> None:
        """Raise ReadOnlyViolation unless the request may be sent."""
        method = method.upper() if isinstance(method, str) else ''
        parts = urlsplit(str(url))
        host = (parts.hostname or '').lower()
        if parts.scheme != 'https':
            raise ReadOnlyViolation('only https requests are allowed')
        if method == 'GET':
            if host != self.api_host:
                raise ReadOnlyViolation('GET requests may only go to the API host')
            if body:
                raise ReadOnlyViolation('GET requests must not have a body')
            return
        if method == 'POST' and self._is_token_request(host, parts.path, body):
            return
        raise ReadOnlyViolation('only GET requests are allowed')

    def _is_token_request(self, host: str, path: str, body) -> bool:
        if not self.allow_token_request or host != self.oauth_host or path.rstrip('/') != '/token':
            return False
        if isinstance(body, bytes):
            body = body.decode('utf-8', 'replace')
        if isinstance(body, str):
            fields = dict(parse_qsl(body))
        elif isinstance(body, dict):
            fields = body
        else:
            return False
        return fields.get('grant_type') == 'client_credentials'

    def charge(self) -> None:
        """Count one request against the budget (raises BudgetExceeded) and keep the interval."""
        now = self._clock()
        if now >= self.deadline:
            raise BudgetExceeded('time budget used up')
        if self.requests_sent >= self.max_requests:
            raise BudgetExceeded('request budget used up')
        if self._last_sent is not None and self.min_interval:
            wait = self._last_sent + self.min_interval - now
            if wait > 0:
                self._sleep(wait)
        self.requests_sent += 1
        self._last_sent = self._clock()

    @staticmethod
    def clamp_url(url: str) -> str:
        """Cap a per_page parameter at MAX_PAGE."""
        def repl(match):
            try:
                value = max(1, min(int(match.group(2)), MAX_PAGE))
            except ValueError:
                value = MAX_PAGE
            return f'{match.group(1)}per_page={value}'
        return _PER_PAGE.sub(repl, url)

    def check_rate_limit(self, response) -> None:
        """Abort instead of sleeping through a long Retry-After (api_call would sleep and retry)."""
        if response.status_code != 429:
            return
        try:
            wait = int(response.headers.get('Retry-After', 1))
        except (TypeError, ValueError):
            wait = 1
        if wait > MAX_RETRY_AFTER or self._clock() + wait >= self.deadline:
            raise BudgetExceeded('rate limited for too long')

    def observe(self, method: str, response) -> None:
        """Remember the status and the top-level field names of the last GET response."""
        if method != 'GET':
            return
        self.last_status = response.status_code
        self.last_keys = None
        if response.status_code == 200 and 'json' in response.headers.get('Content-Type', ''):
            try:
                data = response.json()
            except ValueError:
                return
            if isinstance(data, dict):
                self.last_keys = frozenset(data)


class ReadOnlyAdapter(HTTPAdapter):
    """Transport adapter: the last check before a request goes onto the network."""

    def __init__(self, policy: ReadOnlyPolicy):
        super().__init__(max_retries=0)
        self.policy = policy

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        method = (request.method or '').upper()
        self.policy.check(method, request.url, request.body)
        if method == 'GET':
            request.url = self.policy.clamp_url(request.url)
        self.policy.charge()
        response = super().send(request, stream=stream, timeout=self.policy.timeout,
                                verify=True if verify is False else verify, cert=cert, proxies=proxies)
        # One page per call: without a Link header XurrentApiHelper.api_call does not paginate
        response.headers.pop('Link', None)
        self.policy.check_rate_limit(response)
        self.policy.observe(method, response)
        return response


class ReadOnlySession(requests.Session):
    """Session that checks every request and sends it through ReadOnlyAdapter."""

    def __init__(self, policy: ReadOnlyPolicy):
        super().__init__()
        self._policy = policy
        adapter = ReadOnlyAdapter(policy)
        self.mount('https://', adapter)
        self.mount('http://', adapter)

    def request(self, method, url, *args, **kwargs):
        self._policy.check(method, url, kwargs.get('data', kwargs.get('json')))
        return super().request(method, url, *args, **kwargs)


class ReadOnlyRequests:
    """Stands in for the ``requests`` module inside ``xurrent.core`` while the check runs: every
    request goes through ReadOnlySession; of the rest only exceptions and plain types are passed on."""

    _PASSED_ON = frozenset({'exceptions', 'codes', 'structures', 'Response', 'RequestException',
                            'HTTPError', 'ConnectionError', 'Timeout', 'ConnectTimeout', 'ReadTimeout',
                            '__version__'})

    def __init__(self, policy: ReadOnlyPolicy, real_module=requests):
        self._policy = policy
        self._real = real_module
        self._session = ReadOnlySession(policy)

    def Session(self):  # noqa: N802 - mirrors requests.Session
        return ReadOnlySession(self._policy)

    def request(self, method, url, **kwargs):
        self._policy.check(method, url, kwargs.get('data', kwargs.get('json')))
        return self._session.request(method, url, **kwargs)

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self.request('PUT', url, **kwargs)

    def patch(self, url, **kwargs):
        return self.request('PATCH', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

    def head(self, url, **kwargs):
        return self.request('HEAD', url, **kwargs)

    def options(self, url, **kwargs):
        return self.request('OPTIONS', url, **kwargs)

    def __getattr__(self, name):
        if name in self._PASSED_ON:
            return getattr(self._real, name)
        raise AttributeError(f'{name} is not available in the read-only check')


@contextmanager
def read_only_transport(policy: ReadOnlyPolicy) -> Iterator[ReadOnlyRequests]:
    """Route every HTTP request of xurrent.core through the read-only guard."""
    original = xurrent_core.requests
    guarded = ReadOnlyRequests(policy, requests)
    xurrent_core.requests = guarded
    try:
        yield guarded
    finally:
        xurrent_core.requests = original


class ReadOnlyXurrentApiHelper(XurrentApiHelper):
    """XurrentApiHelper that refuses every method but GET before anything is sent and caps the
    page size and max_results at MAX_PAGE."""

    def api_call(self, uri: str, method='GET', data=None, per_page=100, raw=False,
                 max_results: Optional[int] = None):
        if not isinstance(method, str) or method.upper() != 'GET':
            raise ReadOnlyViolation('only GET requests are allowed')
        if data is not None:
            raise ReadOnlyViolation('GET requests must not have a body')
        if per_page:
            per_page = min(per_page, MAX_PAGE)
        if max_results:
            max_results = min(max_results, MAX_PAGE)
        return super().api_call(uri, 'GET', None, per_page, raw, max_results)


# --------------------------------------------------------------------------------------------------
# Output (only names, statuses, types, numbers and code-like enum values)
# --------------------------------------------------------------------------------------------------

_UNSAFE_NAME = re.compile(r'[^A-Za-z0-9_.:\[\]=,+\-]')
_CODE_VALUE = re.compile(r'^(?=[a-z0-9_\-]*[a-z])[a-z0-9][a-z0-9_\-]{0,47}$')  # needs a letter: no IDs
REDACTED = '<redacted>'
OK, FAIL, SKIP = 'ok', 'FAIL', 'skip'


def safe_name(text, limit: int = 100, spaces: bool = False) -> str:
    """Check, field or exception name (or, with spaces=True, a skip reason) with every unexpected
    character replaced."""
    text = str(text)
    if spaces:
        return ' '.join(_UNSAFE_NAME.sub('?', part) for part in text.split(' '))[:limit]
    return _UNSAFE_NAME.sub('?', text)[:limit]


def safe_code(value) -> str:
    """An enum value as it came if it looks like an API code (e.g. waiting_for_customer), else REDACTED."""
    if isinstance(value, str) and _CODE_VALUE.match(value):
        return value
    return REDACTED


def describe_error(exc: BaseException) -> Tuple[str, Optional[int]]:
    """Exception class name and HTTP status; never the message, which may quote response content."""
    response = getattr(exc, 'response', None)
    status = getattr(response, 'status_code', None)
    if not isinstance(status, int) or isinstance(status, bool):
        status = None
    return type(exc).__name__, status


def _count(value) -> Optional[int]:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


@dataclass
class CheckResult:
    name: str
    status: str
    error_type: Optional[str] = None
    http_status: Optional[int] = None
    count: Optional[int] = None
    fields: Optional[Tuple[int, int, Tuple[str, ...]]] = None  # present, expected, missing names
    reason: Optional[str] = None


class Reporter:
    def __init__(self, out=None, quiet: bool = False):
        self.out = out if out is not None else sys.stdout
        self.quiet = quiet
        self.results: List[CheckResult] = []
        self.enum_findings: Dict[Tuple[str, str], int] = {}   # (field, value) -> occurrences
        self.account_values: Dict[Tuple[str, str], int] = {}  # account-defined enums, information only

    def has_run(self, name: str) -> bool:
        name = safe_name(name)
        return any(result.name == name for result in self.results)

    def ok(self, name: str, count: Optional[int] = None, fields=None) -> CheckResult:
        if fields is not None:
            present, expected, missing = fields
            fields = (_count(present), _count(expected), tuple(safe_name(f, 60) for f in missing))
        return self._add(CheckResult(safe_name(name), OK, count=_count(count), fields=fields))

    def fail(self, name: str, exc: BaseException) -> CheckResult:
        error_type, status = describe_error(exc)
        return self._add(CheckResult(safe_name(name), FAIL, error_type=safe_name(error_type, 60),
                                     http_status=status))

    def skip(self, name: str, reason: str) -> CheckResult:
        return self._add(CheckResult(safe_name(name), SKIP, reason=safe_name(reason, 60, spaces=True)))

    def enum_value(self, field: str, value) -> None:
        key = (safe_name(field, 80), safe_code(value))
        self.enum_findings[key] = self.enum_findings.get(key, 0) + 1

    def account_value(self, field: str, value) -> None:
        key = (safe_name(field, 80), safe_code(value))
        self.account_values[key] = self.account_values.get(key, 0) + 1

    def _add(self, result: CheckResult) -> CheckResult:
        self.results.append(result)
        if not (self.quiet and result.status != FAIL):
            self.write(self.format(result))
        return result

    @staticmethod
    def format(result: CheckResult) -> str:
        parts = [f'{result.status:<5} {result.name}']
        if result.status == FAIL:
            parts.append(result.error_type or 'Error')
            if result.http_status is not None:
                parts.append(f'http={result.http_status}')
        if result.count is not None:
            parts.append(f'n={result.count}')
        if result.fields is not None:
            present, expected, missing = result.fields
            text = f'fields={present}/{expected}'
            if missing:
                text += ' missing=' + ','.join(missing)
            parts.append(text)
        if result.reason:
            parts.append(f'({result.reason})')
        return '  '.join(parts)

    def write(self, line: str) -> None:
        self.out.write(line + '\n')
        self.out.flush()

    def counts(self) -> Dict[str, int]:
        counts = {OK: 0, FAIL: 0, SKIP: 0}
        for result in self.results:
            counts[result.status] += 1
        return counts

    def summary(self, requests_sent: int, seconds: float, aborted: Optional[str] = None) -> str:
        counts = self.counts()
        lines = ['', '=' * 72]
        if self.enum_findings:
            lines.append(f'Unknown enum values ({len(self.enum_findings)} field/value pairs):')
            for (field, value), occurrences in sorted(self.enum_findings.items()):
                lines.append(f'  {field} = {value!r}  ({occurrences}x)')
        if self.account_values:
            lines.append(f'Account-defined enum values not in the SDK enum (information only, '
                         f'{len(self.account_values)}):')
            for (field, value), occurrences in sorted(self.account_values.items()):
                lines.append(f'  {field} = {value!r}  ({occurrences}x)')
        gaps = [r for r in self.results if r.fields and r.fields[2]]
        if gaps:
            lines.append('Expected fields missing in get_by_id/get_me responses:')
            for result in gaps:
                lines.append(f'  {result.name}: ' + ','.join(result.fields[2]))
        failed = [r for r in self.results if r.status == FAIL]
        if failed:
            lines.append('Failed checks:')
            for result in failed:
                lines.append('  ' + self.format(result)[6:])
        reasons: Dict[str, int] = {}
        for result in self.results:
            if result.status == SKIP:
                reasons[result.reason or '?'] = reasons.get(result.reason or '?', 0) + 1
        skipped = ', '.join(f'{reason}: {n}' for reason, n in sorted(reasons.items()))
        lines.append(f'Summary: {len(self.results)} checks: {counts[OK]} ok, {counts[FAIL]} failed, '
                     f'{counts[SKIP]} skipped' + (f' ({skipped})' if skipped else '')
                     + f'; {len(self.enum_findings)} unknown enum values; '
                     f'{_count(requests_sent)} requests in {int(seconds)} s')
        if aborted:
            lines.append(f'ABORTED: {safe_name(aborted, 60, spaces=True)}')
        return '\n'.join(lines)

    def exit_code(self, aborted: Optional[str] = None) -> int:
        if aborted:
            return 2
        return 1 if self.counts()[FAIL] or self.enum_findings else 0


# --------------------------------------------------------------------------------------------------
# Enum and field checks
# --------------------------------------------------------------------------------------------------

_ENUM_OR_RAW = re.compile(r'self\.(\w+)\s*=\s*enum_or_raw\(\s*(\w+)\s*,')
_enum_field_cache: Dict[type, Dict[str, Tuple[type, str]]] = {}


def enum_fields(cls) -> Dict[str, Tuple[type, str]]:
    """Fields of cls that hold an enum: attribute -> (enum class, 'enum_or_raw' or 'annotation').
    Found in the module source (``self.x = enum_or_raw(Enum, ...)``) and in the class annotations."""
    if cls in _enum_field_cache:
        return _enum_field_cache[cls]
    module = sys.modules.get(cls.__module__)
    namespace = vars(module) if module else {}
    fields: Dict[str, Tuple[type, str]] = {}
    for attr, annotation in cls.__dict__.get('__annotations__', {}).items():
        for name in re.findall(r'[A-Za-z_]\w*', annotation if isinstance(annotation, str) else repr(annotation)):
            candidate = namespace.get(name)
            if inspect.isclass(candidate) and issubclass(candidate, enum.Enum):
                fields[attr] = (candidate, 'annotation')
                break
    try:
        source = inspect.getsource(module) if module else ''
    except (OSError, TypeError):
        source = ''
    for attr, enum_name in _ENUM_OR_RAW.findall(source):
        candidate = namespace.get(enum_name)
        if inspect.isclass(candidate) and issubclass(candidate, enum.Enum):
            fields[attr] = (candidate, 'enum_or_raw')
    _enum_field_cache[cls] = fields
    return fields


def walk_records(value, depth: int = 0, seen=None) -> Iterator[JsonSerializableDict]:
    """The records in a result, including referenced records (e.g. Request.workflow)."""
    seen = set() if seen is None else seen
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from walk_records(item, depth, seen)
    elif isinstance(value, JsonSerializableDict) and id(value) not in seen:
        seen.add(id(value))
        yield value
        if depth < 3:
            for key, item in vars(value).items():
                if not key.startswith('_') and isinstance(item, (list, tuple, JsonSerializableDict)):
                    yield from walk_records(item, depth + 1, seen)


def unknown_enum_values(result) -> List[Tuple[str, str, str]]:
    """(Class.field, value, source) for each enum field holding a value its enum does not know."""
    found = []
    for record in walk_records(result):
        for attr, (enum_cls, source) in enum_fields(type(record)).items():
            value = getattr(record, attr, None)
            if type(value) is str and value not in {m.value for m in enum_cls}:
                if enum_cls.__name__ in ACCOUNT_DEFINED_ENUMS:
                    source = 'account-defined'
                found.append((f'{type(record).__name__}.{attr}', value, source))
    return found


def expected_fields(cls) -> List[str]:
    """The named parameters of cls.__init__: the fields the class reads from a record."""
    names = []
    for param in inspect.signature(cls.__init__).parameters.values():
        if param.name in ('self', 'connection_object'):
            continue
        if param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY):
            names.append(param.name)
    return names


# --------------------------------------------------------------------------------------------------
# Discovery
# --------------------------------------------------------------------------------------------------

def domain_classes(package=xurrent) -> Iterator[Tuple[object, type]]:
    """(module, class) for every model with a resource URL in the package."""
    for info in sorted(pkgutil.iter_modules(package.__path__), key=lambda i: i.name):
        module = importlib.import_module(f'{package.__name__}.{info.name}')
        for obj in list(vars(module).values()):
            if (inspect.isclass(obj) and issubclass(obj, JsonSerializableDict)
                    and obj.__module__ == module.__name__ and getattr(obj, '__resourceUrl__', None)):
                yield module, obj


@dataclass
class Method:
    name: str
    kind: str                 # 'class', 'static' or 'instance'
    func: Callable
    params: List[inspect.Parameter]   # without cls/self/connection_object
    takes_connection: bool

    @property
    def required(self) -> List[inspect.Parameter]:
        return [p for p in self.params if p.default is p.empty
                and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)]


def reading_methods(cls) -> List[Method]:
    """The get_* methods defined on cls, except get_by_id."""
    methods = []
    for name, attr in cls.__dict__.items():
        if not name.startswith('get_') or name == 'get_by_id':
            continue
        if isinstance(attr, classmethod):
            kind, func = 'class', attr.__func__
        elif isinstance(attr, staticmethod):
            kind, func = 'static', attr.__func__
        elif inspect.isfunction(attr):
            kind, func = 'instance', attr
        else:
            continue
        params = list(inspect.signature(func).parameters.values())
        if kind in ('class', 'instance'):
            params = params[1:]
        takes_connection = kind != 'instance' and bool(params) and params[0].name == 'connection_object'
        if takes_connection:
            params = params[1:]
        methods.append(Method(name, kind, func, params, takes_connection))
    return methods


def param_enum(module, param: inspect.Parameter):
    """The enum class a parameter is annotated with (e.g. a predefined filter), or None."""
    annotation = param.annotation
    if annotation is param.empty:
        return None
    if inspect.isclass(annotation):
        return annotation if issubclass(annotation, enum.Enum) else None
    for name in re.findall(r'[A-Za-z_]\w*', str(annotation)):
        candidate = vars(module).get(name)
        if inspect.isclass(candidate) and issubclass(candidate, enum.Enum):
            return candidate
    return None


def variants(module, method: Method, required: dict) -> Iterator[Tuple[str, dict]]:
    """(label, kwargs) for each call of a method: the plain call, each filter value, each boolean
    switch turned on, and for get_notes the newest note only."""
    names = {p.name for p in method.params}
    base = dict(required)
    if 'max_results' in names:
        base['max_results'] = LIST_MAX_RESULTS
    yield '', base
    for param in method.params:
        if param.name in required:
            continue
        enum_cls = param_enum(module, param)
        if enum_cls is not None:
            for member in enum_cls:
                yield str(member.value), {**base, param.name: member}
        elif param.default is False:
            yield param.name, {**base, param.name: True}
    if method.name == 'get_notes' and 'sort' in names:
        newest = {**required, 'sort': '-created_at'}
        if 'max_results' in names:
            newest['max_results'] = 1
        yield 'sort=-created_at', newest


class Skip(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _snake(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def _first_id(items) -> Optional[object]:
    if isinstance(items, list) and items:
        first = items[0]
        value = first.get('id') if isinstance(first, dict) else getattr(first, 'id', None)
        return value
    return None


def _template_id(tasks) -> Optional[object]:
    for task in tasks or []:
        template = getattr(task, 'template', None)
        value = template.get('id') if isinstance(template, dict) else getattr(template, 'id', None)
        if value:
            return value
    return None


def _duration_window() -> dict:
    start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    fmt = '%Y-%m-%dT%H:%M:%SZ'
    return {'start': start.strftime(fmt), 'end': (start + timedelta(days=7)).strftime(fmt)}


# Arguments that cannot be derived from the parameter name alone: (class, method) -> builder
RECIPES: Dict[Tuple[str, str], Callable[[], dict]] = {
    ('Calendar', 'get_duration'): _duration_window,
}


def resolve_argument(cls, method: Method, param: str, record, cache: dict, connection=None):
    """Value for a required argument, taken from the record or earlier results; raises Skip."""
    recipe = RECIPES.get((cls.__name__, method.name))
    if recipe and param in recipe():
        return recipe()[param]
    if record is None:
        raise Skip('no record')
    snake = _snake(cls.__name__)
    if param in ('id', f'{snake}_id', f'{snake.replace("_", "")}ID', f'{cls.__name__[0].lower()}{cls.__name__[1:]}ID'):
        return record.id
    if param == 'note_id':
        value = _first_id(cache.get('get_notes'))
        if value is None:
            raise Skip('no note')
        return value
    if param == 'templateID':
        if 'templateID' not in cache:
            tasks = cache.get('get_tasks') or []
            value = _template_id(tasks)
            if value is None and tasks and connection is not None:
                # Task lists do not include the template; the full task does
                from xurrent.tasks import Task
                value = _template_id([Task.get_by_id(connection, tasks[0].id)])
            cache['templateID'] = value
        if cache['templateID'] is None:
            raise Skip('no task template')
        return cache['templateID']
    raise Skip('no recipe')


# --------------------------------------------------------------------------------------------------
# Running
# --------------------------------------------------------------------------------------------------

class Runner:
    def __init__(self, connection: XurrentApiHelper, reporter: Reporter, policy: ReadOnlyPolicy):
        self.connection = connection
        self.reporter = reporter
        self.policy = policy

    def run(self, name: str, call: Callable, expected: Optional[List[str]] = None):
        """Run one check; returns its result, or None if it failed or was skipped."""
        if name in KNOWN_SKIPS:
            self.reporter.skip(name, KNOWN_SKIPS[name])
            return None
        self.policy.last_keys = None
        try:
            result = call()
        except (BudgetExceeded, KeyboardInterrupt):
            raise
        except Exception as exc:  # noqa: BLE001 - every failure is reported by its type only
            self.reporter.fail(name, exc)
            return None
        count = len(result) if isinstance(result, (list, tuple)) else (0 if result is None else 1)
        fields = None
        if expected is not None and isinstance(result, JsonSerializableDict) and self.policy.last_keys is not None:
            missing = tuple(f for f in expected if f not in self.policy.last_keys)
            fields = (len(expected) - len(missing), len(expected), missing)
        for field, value, source in unknown_enum_values(result):
            if source == 'account-defined':
                self.reporter.account_value(field, value)
            else:
                self.reporter.enum_value(field, value)
        self.reporter.ok(name, count=count, fields=fields)
        return result

    def invoke(self, cls, method: Method, record, kwargs: dict):
        if method.kind == 'instance':
            return method.func(record, **kwargs)
        args = (self.connection,) if method.takes_connection else ()
        if method.kind == 'class':
            return method.func(cls, *args, **kwargs)
        return method.func(*args, **kwargs)

    def check_core(self) -> None:
        connection = self.connection
        self.run('core.search[test]', lambda: connection.search('test', max_results=3))
        self.run('core.list_archive', connection.list_archive)
        self.run('core.list_trash', connection.list_trash)
        self.run('core.list_audit_lines', connection.list_audit_lines)

    def check_class(self, module, cls) -> None:
        cname = cls.__name__
        methods = reading_methods(cls)
        record = None
        # List functions and other class/static methods without required arguments
        for method in [m for m in methods if m.kind != 'instance' and not m.required]:
            for label, kwargs in variants(module, method, {}):
                name = f'{cname}.{method.name}' + (f'[{label}]' if label else '')
                if self.reporter.has_run(name):
                    continue
                single = method.name in ('get_me',)
                result = self.run(name, lambda m=method, k=kwargs: self.invoke(cls, m, None, k),
                                  expected=expected_fields(cls) if single else None)
                if record is None and isinstance(result, list) and result and isinstance(result[0], cls):
                    record = result[0]
        # get_by_id on the first record
        detail = None
        if 'get_by_id' in cls.__dict__:
            if record is None:
                self.reporter.skip(f'{cname}.get_by_id', 'no record')
            else:
                detail = self.run(f'{cname}.get_by_id', lambda: cls.get_by_id(self.connection, record.id),
                                  expected=expected_fields(cls))
        instance = detail if isinstance(detail, cls) else record
        # Sub-resources and id-based class/static methods; those without required arguments first,
        # so that later recipes can use their results (e.g. the first note for get_note_by_id)
        cache: dict = {}
        rest = [m for m in methods if m.kind == 'instance' or m.required]
        rest.sort(key=lambda m: bool(m.required))
        for method in rest:
            base_name = f'{cname}.{method.name}'
            if instance is None:
                self.reporter.skip(base_name, 'no record')
                continue
            try:
                required = {p.name: resolve_argument(cls, method, p.name, instance, cache, self.connection)
                            for p in method.required}
            except Skip as skip:
                self.reporter.skip(base_name, skip.reason)
                continue
            except (BudgetExceeded, KeyboardInterrupt):
                raise
            except Exception as exc:  # noqa: BLE001 - a failed lookup fails the check that needs it
                self.reporter.fail(base_name, exc)
                continue
            for label, kwargs in variants(module, method, required):
                name = base_name + (f'[{label}]' if label else '')
                result = self.run(name, lambda m=method, k=kwargs: self.invoke(cls, m, instance, k))
                if not label:
                    cache[method.name] = result


# --------------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------------

@dataclass
class Credentials:
    api_url: str
    account: str
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    @property
    def oauth(self) -> bool:
        return self.api_key is None


def load_credentials(environ) -> Optional[Credentials]:
    if all(environ.get(k) for k in ('APITOKEN', 'APIACCOUNT', 'APIURL')):
        return Credentials(environ['APIURL'], environ['APIACCOUNT'], api_key=environ['APITOKEN'])
    if all(environ.get(k) for k in ('XURRENT_CLIENT_ID', 'XURRENT_CLIENT_SECRET', 'XURRENT_ACCOUNT', 'XURRENT_API_URL')):
        return Credentials(environ['XURRENT_API_URL'], environ['XURRENT_ACCOUNT'],
                           client_id=environ['XURRENT_CLIENT_ID'], client_secret=environ['XURRENT_CLIENT_SECRET'])
    return None


def silent_logger() -> logging.Logger:
    """Logger for the helper: api_call logs response texts and URLs with IDs, so nothing is emitted."""
    logger = logging.getLogger('xurrent.read_only_check')
    logger.handlers[:] = [logging.NullHandler()]
    logger.propagate = False
    logger.setLevel(logging.CRITICAL + 1)
    return logger


def connect(credentials: Credentials, policy: ReadOnlyPolicy) -> ReadOnlyXurrentApiHelper:
    return ReadOnlyXurrentApiHelper(
        credentials.api_url, api_key=credentials.api_key, api_account=credentials.account,
        resolve_user=False, logger=silent_logger(), client_id=credentials.client_id,
        client_secret=credentials.client_secret, timeout=policy.timeout)


def _quiet_excepthook(exc_type, exc, tb):
    sys.stderr.write(f'aborted: {safe_name(exc_type.__name__, 60)}\n')


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='Read-only smoke check of the SDK against a real Xurrent account.')
    parser.add_argument('--quiet', action='store_true', help='print only failed checks and the summary')
    parser.add_argument('--max-seconds', type=float, default=DEFAULT_MAX_SECONDS)
    parser.add_argument('--max-requests', type=int, default=DEFAULT_MAX_REQUESTS)
    parser.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT, help='seconds per HTTP request')
    parser.add_argument('--min-interval', type=float, default=MIN_INTERVAL, help='seconds between two requests')
    return parser.parse_args(argv)


def run_checks(connection, reporter: Reporter, policy: ReadOnlyPolicy) -> Optional[str]:
    """Run every check; returns why the run was aborted, or None."""
    runner = Runner(connection, reporter, policy)
    from xurrent.people import Person
    me = runner.run('Person.get_me', lambda: Person.get_me(connection), expected=expected_fields(Person))
    if me is None:
        return 'get_me failed'
    runner.check_core()
    for module, cls in domain_classes():
        runner.check_class(module, cls)
    return None


def main(argv=None, environ=None, out=None) -> int:
    args = parse_args(argv)
    if environ is None:
        environ = os.environ
        if load_credentials(environ) is None:
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass
    reporter = Reporter(out, quiet=args.quiet)
    credentials = load_credentials(environ)
    if credentials is None:
        reporter.write('Missing credentials: set APITOKEN, APIACCOUNT, APIURL or XURRENT_CLIENT_ID, '
                       'XURRENT_CLIENT_SECRET, XURRENT_ACCOUNT, XURRENT_API_URL.')
        return 2
    policy = ReadOnlyPolicy(credentials.api_url, allow_token_request=credentials.oauth,
                            max_requests=args.max_requests, max_seconds=args.max_seconds, timeout=args.timeout,
                            min_interval=args.min_interval)
    reporter.write(f'Read-only smoke check ({"OAuth" if credentials.oauth else "API token"}); '
                   f'budget {args.max_requests} requests / {int(args.max_seconds)} s')
    previous_hook = sys.excepthook
    sys.excepthook = _quiet_excepthook
    logging.disable(logging.CRITICAL)
    aborted = None
    try:
        with read_only_transport(policy):
            try:
                connection = connect(credentials, policy)
            except (BudgetExceeded, KeyboardInterrupt):
                raise
            except Exception as exc:  # noqa: BLE001
                reporter.fail('core.connect', exc)
                connection = None
                aborted = 'login failed'
            if connection is not None:
                aborted = run_checks(connection, reporter, policy)
    except BudgetExceeded:
        aborted = 'budget used up'
    except KeyboardInterrupt:
        aborted = 'interrupted'
    except Exception as exc:  # noqa: BLE001
        aborted = f'unexpected {type(exc).__name__}'
    finally:
        logging.disable(logging.NOTSET)
        sys.excepthook = previous_hook
    reporter.write(reporter.summary(policy.requests_sent, time.monotonic() - policy.started, aborted))
    return reporter.exit_code(aborted)


if __name__ == '__main__':
    sys.exit(main())
