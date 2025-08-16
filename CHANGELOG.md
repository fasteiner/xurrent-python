# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
