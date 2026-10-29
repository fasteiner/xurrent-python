# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`xurrent-python` is a Python wrapper for the Xurrent API (a service/incident management platform). It provides object-oriented abstractions over REST endpoints with built-in handling for authentication, pagination, rate limiting, and OAuth token refresh.

## Setup

This project uses [Poetry](https://python-poetry.org/) for dependency management.

```bash
pip install poetry
poetry install --with dev
eval $(poetry env activate)
pre-commit install
```

## Commands

### Testing

```bash
# Unit tests (no credentials required)
pytest ./tests/unit_tests

# Run a single test file
pytest ./tests/unit_tests/test_core_oauth.py -v

# Run a single test function
pytest ./tests/unit_tests/test_core_oauth.py::test_init_requires_authentication_method -v

# Doctests in source modules
pytest ./src/ --doctest-modules -v

# Integration tests (requires env vars: APITOKEN, APIACCOUNT, APIURL)
pytest ./tests/integration
```

Integration tests require a `.env` file or environment variables: `APITOKEN`, `APIACCOUNT`, `APIURL`.

### Pre-commit

```bash
pre-commit run --all-files
```

The pre-commit hook runs the unit test suite automatically before each commit.

## Architecture

### Core (`xurrent/core.py`)

`XurrentApiHelper` is the central HTTP client. It:
- Supports two auth modes: **API key** (`XurrentApiHelper(token=..., account=..., api_url=...)`) and **OAuth 2.0 client credentials** (`XurrentApiHelper(client_id=..., client_secret=..., account=..., api_url=...)`)
- Automatically handles pagination via `Link` response headers — callers receive aggregated results
- Retries on HTTP 429 (rate limit) and refreshes OAuth tokens on HTTP 401
- Exposes `api_call(method, url, data, params)` as the low-level HTTP wrapper used by all domain classes

`JsonSerializableDict` is the base class for all resource models, providing `to_dict()` and `to_json()` serialization.

### Domain Classes

Each module wraps one Xurrent resource type. All domain classes follow the same patterns:
- Accept a `XurrentApiHelper` instance as `connection_object`
- Use `@classmethod` factory methods (`get_by_id()`, `get_<resource>()`, `create()`) to deserialize API responses into instances via `from_data()`
- Expose lifecycle methods (enable/disable/archive/trash/restore) and resource-specific operations

| Module | Class | Notable Features |
|---|---|---|
| `requests.py` | `Request` | Notes, linked CIs, status/category/completion enums |
| `people.py` | `Person` | `get_me()`, team membership |
| `configuration_items.py` | `ConfigurationItem` | Auto-increments label on creation |
| `tasks.py` | `Task` | Approve/reject/cancel, workflow linkage |
| `workflows.py` | `Workflow` | Close with completion reason |
| `teams.py` | `Team` | Basic lifecycle management |

### Circular Import Handling

Domain classes cross-reference each other (e.g., `Request` embeds `Person`, `Team`, `Workflow`). To avoid circular imports, these are imported lazily — inside methods rather than at module top level. When adding new cross-module references, follow this same pattern.

### Tests

- **`tests/unit_tests/`** — Uses `MagicMock` to stub `XurrentApiHelper`; no real credentials needed
- **`tests/integration/`** — Hits a live Xurrent instance; requires credentials in environment

When adding a new domain class, add corresponding unit tests under `tests/unit_tests/`.

## Changelog

All changes must be documented in [CHANGELOG.md](CHANGELOG.md) under the `[Unreleased]` section, following the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format. Use the appropriate subsection (`Added`, `Changed`, `Fixed`, `Removed`) and prefix each entry with the affected module or component (e.g., `Core:`, `Requests:`).
