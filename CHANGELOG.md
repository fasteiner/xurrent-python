# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Problems: added `Problem` class with `ProblemPredefinedFilter`, `ProblemStatus`, and `ProblemImpact` enums; supports CRUD, archive/trash/restore, and sub-resources (requests, workflows, notes).
- ServiceInstances: added `ServiceInstance` class with `ServiceInstancePredefinedFilter` and `ServiceInstanceStatus` enums; supports CRUD and sub-resources (cis, slas, users).
- Releases: added `Release` class with `ReleasePredefinedFilter`, `ReleaseStatus`, and `ReleaseImpact` enums; supports CRUD, archive/trash/restore, and sub-resources (workflows, notes).
- Projects: added `Project` class with `ProjectPredefinedFilter`, `ProjectStatus`, and `ProjectCategory` enums; supports CRUD, archive/trash/restore, and sub-resources (tasks, phases, workflows, risks, notes).
- Contracts: added `Contract` class with `ContractPredefinedFilter` and `ContractStatus` enums; supports CRUD and CI listing.
- KnowledgeArticles: added `KnowledgeArticle` class with `KnowledgeArticlePredefinedFilter` and `KnowledgeArticleStatus` enums; supports CRUD, archive/trash/restore, and sub-resources (requests, service_instances, translations).
- Risks: added `Risk` class with `RiskPredefinedFilter`, `RiskStatus`, and `RiskSeverity` enums; supports CRUD, archive/trash/restore, and sub-resources (organizations, projects, services).
- ServiceOfferings: added `ServiceOffering` class with `ServiceOfferingPredefinedFilter` and `ServiceOfferingStatus` enums; supports CRUD.
- SkillPools: added `SkillPool` class with `SkillPoolPredefinedFilter` enum; supports CRUD, enable/disable, and sub-resources (members, effort_classes).
- Requests: added `get_attachments`, `get_knowledge_articles`, `get_automation_rules`, `get_satisfaction_feedback`, `get_tags`, and `get_watches` instance methods.
- Tasks: added `get_notes`, `add_note`, `get_approvals`, `get_cis`, `get_predecessors`, `get_successors`, `get_service_instances`, and `get_automation_rules` instance methods.
- Workflows: added `get_notes`, `add_note`, `get_automation_rules`, `get_phases`, `get_requests`, and `get_problems` instance methods.
- People: added `get_cis`, `get_addresses`, `get_contacts`, `get_permissions`, `get_ci_coverages`, `get_sla_coverages`, `get_service_coverages`, `get_out_of_office_periods`, and `get_skill_pools` instance methods.
- Organizations: added `get_addresses`, `get_contacts`, `get_contracts`, `get_risks`, `get_slas`, and `get_time_allocations` instance methods.
- Services: added `get_workflows`, `get_request_templates`, `get_risks`, `get_service_instances`, `get_slas`, and `get_service_offerings` instance methods.
- Calendars: added `get_duration`, `get_hours`, and `get_holidays` instance methods.
- Teams: added `get_service_instances` instance method.
- Holidays: added `get_calendars` instance method.
- ClosureCodes: added `ClosureCode` class; supports CRUD.
- Core: added `search(query, types)` for cross-resource full-text search via `GET /search`.
- Core: added `bulk_import(data, import_type, import_format)` for CSV/TSV bulk imports via `POST /import`.
- Core: added `list_archive(queryfilter)` to list all archived items via `GET /archive`.
- Core: added `list_trash(queryfilter)` to list all trashed items via `GET /trash`.
- Core: added `list_audit_lines(queryfilter)` to query the global audit log via `GET /audit_lines`.
- Docs: added `CLAUDE.md` with setup instructions, test commands, architecture overview, and changelog requirements for Claude Code.
- Products: added `Product` class with `ProductPredefinedFilter` and `ProductDepreciationMethod` enums; supports CRUD, enable/disable, and CI listing.
- ProductCategories: added `ProductCategory` class with `ProductCategoryRuleSet` enum; supports CRUD and enable/disable.
- Organizations: added `Organization` class with `OrganizationPredefinedFilter` enum; supports CRUD, enable/disable, archive/trash/restore, people and child org listing.
- Sites: added `Site` class with `SitePredefinedFilter` enum; supports CRUD, enable/disable, archive/trash/restore.
- OutOfOfficePeriods: added `OutOfOfficePeriod` class with `OutOfOfficePeriodPredefinedFilter` enum; supports CRUD and DELETE.
- Holidays: added `Holiday` class; supports CRUD.
- CustomCollections: added `CustomCollection` class with `CustomCollectionPredefinedFilter` enum; supports CRUD, enable/disable, and element listing.
- CustomCollectionElements: added `CustomCollectionElement` class with `CustomCollectionElementPredefinedFilter` enum; supports CRUD and enable/disable.
- ShopArticleCategories: added `ShopArticleCategory` class with `ShopArticleCategoryPredefinedFilter` enum; supports CRUD.
- ShopArticles: added `ShopArticle` class with `ShopArticlePredefinedFilter` and `ShopArticleRecurringPeriod` enums; supports CRUD and enable/disable.
- ShopOrderLines: added `ShopOrderLine` class with `ShopOrderLinePredefinedFilter`, `ShopOrderLineStatus`, and `ShopOrderLineRecurringPeriod` enums; supports CRUD.
- Services: added `Service` class with `ServicePredefinedFilter` enum; supports CRUD and enable/disable.
- Calendars: added `Calendar` class with `CalendarPredefinedFilter` enum; supports CRUD and enable/disable.
- TimeAllocations: added `TimeAllocation` class with `TimeAllocationPredefinedFilter` and category enums; supports CRUD and enable/disable.
- EffortClasses: added `EffortClass` class with `EffortClassPredefinedFilter` enum; supports CRUD and enable/disable.
- RequestTemplates: added `RequestTemplate` class with `RequestTemplatePredefinedFilter`, `RequestTemplateCategory`, `RequestTemplateStatus`, and `RequestTemplateImpact` enums; supports CRUD and enable/disable.
- UiExtensions: added `UiExtension` class with `UiExtensionCategory` enum; supports CRUD and enable/disable.
- WorkflowTemplates: added `WorkflowTemplate` class with `WorkflowTemplatePredefinedFilter` and `WorkflowTemplateCategory` enums; supports CRUD and enable/disable.

### Changed

- People: `Person` now deserializes `site` (→ `Site`) and `organization` (→ `Organization`) references; also fixed a `People.from_data` typo in `update()`.
- ConfigurationItems: `ConfigurationItem` now deserializes the `product` reference (→ `Product`).
- Products: `Product` now deserializes the `category` reference (→ `ProductCategory`).
- CI: updated GitHub Actions in `release.yml` — `GitTools/actions` `v0` → `v3` (latest version compatible with GitVersion 5.x; v4+ requires GitVersion ≥6.1), `stefanzweifel/git-auto-commit-action` `v5` → `v7`, `softprops/action-gh-release` `v1` → `v2`.
- CI: updated `python-package.yml` — `actions/setup-python` `v3` → `v5`; added `pip install .` so the package itself is installed before tests run; added a `flake8` lint step (syntax errors and undefined names only); split test run into separate `Unit tests` and `Integration tests` steps so unit tests always run regardless of credentials; added Python 3.14 to the test matrix.

### Fixed

- Core/People/Requests/Tasks/Workflows: restored lazy-loaded cross-module references in type annotations and fixed `Task` sub-resource helper name resolution so flake8 no longer reports `F821` undefined names.

## [0.11.0] - 2026-04-13

### Added


- Core: support OAuth client credentials authentication via `client_id` and `client_secret` in `XurrentApiHelper` while maintaining API key compatibility.
- Core: The OAuth token endpoint now dynamically determines the domain from `base_url`, preserving any regional subdomains to ensure consistency between API and OAuth endpoints.
- Core: When using OAuth, if a 401 Unauthorized error is received, the token is automatically refreshed and the API call is retried once. If authentication still fails after token refresh, an explicit HTTPError is raised.

## [0.10.0] - 2025-08-16

### Added

- Core: Added bulk\_export() function to dowload bulk record data

### Changed

- Core: Switched to a requests.session object to enable persistent connection recycling.
- Core: Provide options to disable pagination and prevent api result's JSON parsing (in association with bulk\_export).

### Fixed

- Core: do not prepend the base\_url to the uri of an api\_call if a protocol is already included (i.e. uri is already fully-formed).

## [0.9.1] - 2025-06-13

### Changed

#### `.github/workflows/release.yml`

- Introduced a new step `Determine Effective Version` to compute a more accurate version number depending on whether Python files were changed:
  - If Python files changed, uses `gitversion`'s semantic version (`semVer`).
  - If no Python files changed, forces a patch bump based on the previous tag.
- The `effective_version` output is now used consistently across:
  - The `Update CHANGELOG.md` step.
  - The commit message for updating `pyproject.toml`.
  - The Git tag and GitHub Release.
  - The `pyproject.toml` version field.
- Adjusted the condition for the `Build release distributions` step to run only if Python files changed.
- Simplified and cleaned up various comments in the workflow for better readability and maintainability.

## [0.9.0] - 2025-06-13

### Changed

- **GitHub Actions Workflow**
  - Modified the version bump logic in `.github/workflows/release.yml` to apply major/minor/patch logic only if Python files have changed. If no Python files changed, the workflow now forces a patch bump to prevent unintended major or minor releases.

## [0.8.0] - 2025-06-13

### Added

- Added a step to detect if any Python files were changed (`check-python-changes`) in the release workflow.

- The `release` and `publish to PyPI` steps now only run if Python files were changed.

- The workflow now supports Python 3.12 and Python 3.13 in addition to 3.9–3.11.

- In the Dev Container:
  - Added GitHub Actions support extension.
  - Added VSCode Icons extension.
  - Added Markdown All in One extension.
  - Added Markdown Checkbox extension.
  - Added Markdown Preview GitHub Styles extension.

- In the VSCode workspace recommendations:
  - Added GitHub Actions extension to `.vscode/extensions.json`.

### Changed

- Improved release workflow logic to skip release and publish steps if no Python files were changed.

## [0.7.0] - 2025-06-13

### Added

#### `.devcontainer/devcontainer.json`

- Introduced a new Visual Studio Code **development container** configuration to streamline the development environment.
  - Uses the base Ubuntu image from Microsoft's devcontainers.
  - Adds common development utilities via `common-utils` feature.
  - Installs VS Code extensions:
    - `elagil.pre-commit-helper`
    - `ms-python.python`
  - Runs `.devcontainer/setup.sh` post container creation for environment setup.

#### `.devcontainer/setup.sh`

- Added a setup script for the development container:
  - Installs **Poetry** package manager.
  - Installs all project dependencies, including development dependencies.
  - Activates the Poetry virtual environment and opens a shell.
  - Installs **pre-commit hooks** for code quality enforcement.

### Changed

#### `Contributing.md`

- Updated instructions for activating the Poetry virtual environment:
  - Changed from `poetry shell` to `eval $(poetry env activate)` for improved shell compatibility and automation.

#### `README.md`

- Added badges to the top of the README for enhanced project visibility:
  - **PyPI version** badge.
  - **PyPI downloads** badge.
  - **GPL v3 License** badge.

#### `pyproject.toml`

- Added new dependency:
  - `shell` package (`^1.0.1`) for enhanced shell scripting and command execution capabilities within the project.

## [0.6.0] - 2025-02-24

### Changed

- Ensure that version numbers in ChangeLog and releases are in sync

## [0.5.0] - 2025-02-24

### Changed

- Corrected ReadMe links

## [0.4.0] - 2025-02-24

### Added

- Add automatic release notes generation, github release
- Build fully automated release on push on main

### Changed

- Switch to using "Keep a Changelog" ChangeLog format
- Change versioning to use semantic versioning (change log had to be updated as well)

## [0.0.2-beta.12] - 2025-02-12

### Added

- configuration\_items: add class ConfigurationItem
- configuration\_items: add static methods: get\_configuration\_items, get\_by\_id
- Request: add class method get\_cis\_by\_request\_id to retrieve configuration items associated with a request by its ID.
- Request: add class method add\_cis\_to\_request\_by\_id to link configuration items to a request by its ID.
- Request: add class method remove\_cis\_from\_request\_by\_id to unlink configuration items from a request by its ID.
- Request: add instance method get\_cis to retrieve configuration items associated with the current request instance.
- Request: add instance method add\_cis to link configuration items to the current request instance.
- Request: add instance method remove\_cis to unlink configuration items from the current request instance.

### Bug Fixes

- Core: fix issue where 204 status code was not handled correctly
- Core: paging, ensure that '<>' gets removed

## [0.0.2-beta.11] - 2025-01-08

### Added

- Core: add function decode\_api\_id and encode\_api\_id to convert between nodeID and normal ID

## [0.0.2-beta.10] - 2024-12-18

### Added

- Core: add enum LogLevel
- Core: add method set\_log\_level to change the log level

### Breaking Changes

- Core: init: parameter for logger has been added, if not provided, a new logger will be created

## [0.0.2-beta.9] - 2024-12-11

### Added

- Request, Workflow, Task, Person, Team: add non static methods: ref\_str() --> return a reference string
- Request: add RequestCategory enum
- core: JSONSerializableDict: handle datetime and list of objects
- Workflow: add WorkflowCategory enum
- Workflow: use WorkflowCategory and WorkflowStatus enums on instantiation
- Team: add Team class
- Team: add enum TeamPredefinedFilter
- People: add non static methods: get\_teams
- Tests: add tests for Request
- Tests: add pre-commit hooks yaml file

### Fixed

- Person, Workflow, Task: inherit JsonSerializableDict --> make serializable
- Request: close: make it possible to close a without a note (using default note)

### Breaking Changes

- Request: request.created\_by, request.requested\_by, request.requested\_for, request.member are now Person objects
- Workflow: workflow.manager is now a Person object

## [0.0.2-beta.8] - 2024-12-10

### Fixed

- Core: \_\_append\_per\_page: exclude auto append for /me

### Breaking Changes

- Request: request.workflow is now a Workflow object instead of a dict --> request.workflow.id instead of request.workflow\['id']

## [0.0.2-beta.7] - 2024-12-10

### Bug Fixes

- Task: `__update_object__` fixed

## [0.0.2-beta.6] - 2024-12-10

### Bug Fixes

- Task: Fix update method

## [0.0.2-beta.5] - 2024-12-10

### Bug Fixes

- Task: Fix update method

## [0.0.2-beta.4] - 2024-12-10

### Added

- People: add non static methods: enable, archive, trash, restore
- People: add static methods: create, get\_people
- Workflows: add static methods: get\_workflows

## [0.0.2-beta.3] - 2024-12-06

### Added

- Task: add non static methods: get\_workflow, close, approve, reject, cancel, create
- Workflow: add non static methods: create\_task

## [0.0.2-beta.2] - 2024-12-06

### Added

- Task: add base functionality for tasks
- Workflow: add methods: get\_task\_by\_template\_id, get\_tasks
- Workflow: update: add check for possible status values
- Request: add static method: update\_by\_id

### Bug Fixes

- Workflow: Fix toString / **str** method

### Breaking Changes

- Request: renamed get\_request to get\_requests
- Workflow: get\_workflow\_task\_by\_template\_id now returns a Task object List

## [0.0.2-beta.1] - 2024-12-06

### Added

- Workflow: add base functionality for workflows
- People: add base functionality for people
- core: automatically get api user person object (optional, default: True)

## [0.0.2-beta.0] - 2024-12-05

### Added

- Request: add methods: archive, trash, restore

### Bug Fixes

- Request: Fix get\_request, get\_notes method

## [0.0.1] - 2024-12-05

### Added

- Pagination: auto pagination get requests
- Retry-after: auto retry after 429 status code
- custom fields conversion (from and to object/dict)

[0.11.0]: https://github.com/fasteiner/xurrent-python/compare/v0.10.0...v0.11.0

[0.10.0]: https://github.com/fasteiner/xurrent-python/compare/v0.9.1...v0.10.0

[0.9.1]: https://github.com/fasteiner/xurrent-python/compare/v0.9.0...v0.9.1

[0.9.0]: https://github.com/fasteiner/xurrent-python/compare/v0.8.0...v0.9.0

[0.8.0]: https://github.com/fasteiner/xurrent-python/compare/v0.7.0...v0.8.0

[0.7.0]: https://github.com/fasteiner/xurrent-python/compare/v0.6.0...v0.7.0

[0.6.0]: https://github.com/fasteiner/xurrent-python/compare/v0.5.0...v0.6.0

[0.5.0]: https://github.com/fasteiner/xurrent-python/compare/v0.4.0...v0.5.0

[0.4.0]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.12...v0.4.0

[0.0.2-beta.12]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.11...v0.0.2-beta.12

[0.0.2-beta.11]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.10...v0.0.2-beta.11

[0.0.2-beta.10]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.9...v0.0.2-beta.10

[0.0.2-beta.9]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.8...v0.0.2-beta.9

[0.0.2-beta.8]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.7...v0.0.2-beta.8

[0.0.2-beta.7]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.6...v0.0.2-beta.7

[0.0.2-beta.6]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.5...v0.0.2-beta.6

[0.0.2-beta.5]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.4...v0.0.2-beta.5

[0.0.2-beta.4]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.3...v0.0.2-beta.4

[0.0.2-beta.3]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.2...v0.0.2-beta.3

[0.0.2-beta.2]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.1...v0.0.2-beta.2

[0.0.2-beta.1]: https://github.com/fasteiner/xurrent-python/compare/v0.0.2-beta.0...v0.0.2-beta.1

[0.0.2-beta.0]: https://github.com/fasteiner/xurrent-python/compare/v0.0.1...v0.0.2-beta.0

[0.0.1]: https://github.com/fasteiner/xurrent-python/releases/tag/v0.0.1
