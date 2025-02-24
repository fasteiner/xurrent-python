# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add automatic release notes generation, github release
- Build fully automated release on push on main

### Changed

- Switch to using "Keep a Changelog" ChangeLog format
- Change versioning to use semantic versioning (change log had to be updated as well) 

## [v0.0.2-beta.12] - 2025-02-12

### Added

- configuration_items: add class ConfigurationItem
- configuration_items: add static methods: get_configuration_items, get_by_id
- Request: add class method get_cis_by_request_id to retrieve configuration items associated with a request by its ID.
- Request: add class method add_cis_to_request_by_id to link configuration items to a request by its ID.
- Request: add class method remove_cis_from_request_by_id to unlink configuration items from a request by its ID.
- Request: add instance method get_cis to retrieve configuration items associated with the current request instance.
- Request: add instance method add_cis to link configuration items to the current request instance.
- Request: add instance method remove_cis to unlink configuration items from the current request instance.

### Bug Fixes

- Core: fix issue where 204 status code was not handled correctly
- Core: paging, ensure that '<>' gets removed


## [v0.0.2-beta.11] - 2025-01-08

### Added

- Core: add function decode_api_id and encode_api_id to convert between nodeID and normal ID

## [v0.0.2-beta.10] - 2024-12-18

### Added

- Core: add enum LogLevel
- Core: add method set_log_level to change the log level

### Changed

- Core: init: parameter for logger has been added, if not provided, a new logger will be created

## [v0.0.2-beta.9] - 2024-12-11

### Added

- Request, Workflow, Task, Person, Team: add non static methods: ref_str() --> return a reference string
- Request: add RequestCategory enum
- core: JSONSerializableDict: handle datetime and list of objects
- Workflow: add WorkflowCategory enum
- Workflow: use WorkflowCategory and WorkflowStatus enums on instantiation
- Team: add Team class
- Team: add enum TeamPredefinedFilter
- People: add non static methods: get_teams
- Tests: add tests for Request
- Tests: add pre-commit hooks yaml file

### Fixed

- Person, Workflow, Task: inherit JsonSerializableDict --> make serializable
- Request: close: make it possible to close a without a note (using default note)

### Changed

- Request: request.created_by, request.requested_by, request.requested_for, request.member are now Person objects
- Workflow: workflow.manager is now a Person object

## [v0.0.2-beta.8] - 2024-12-10

### Fixed

- Core: __append_per_page: exclude auto append for /me

### Changed

- Request: request.workflow is now a Workflow object instead of a dict --> request.workflow.id instead of request.workflow['id']

## [v0.0.2-beta.7] - 2024-12-10

### Bug Fixes

- Task: `__update_object__` fixed

## [v0.0.2-beta.6] - 2024-12-10

### Bug Fixes

- Task: Fix update method

## [v0.0.2-beta.5] - 2024-12-10

### Bug Fixes

- Task: Fix update method

## [v0.0.2-beta.4] - 2024-12-10

### Added

- People: add non static methods: enable, archive, trash, restore
- People: add static methods: create, get_people
- Workflows: add static methods: get_workflows

## [v0.0.2-beta.3] - 2024-12-06

### Added

- Task: add non static methods: get_workflow, close, approve, reject, cancel, create
- Workflow: add non static methods: create_task

## [v0.0.2-beta.2] - 2024-12-06

### Added

- Task: add base functionality for tasks
- Workflow: add methods: get_task_by_template_id, get_tasks
- Workflow: update: add check for possible status values
- Request: add static method: update_by_id

### Bug Fixes

- Workflow: Fix toString / __str__ method

### Changed

- Request: renamed get_request to get_requests
- Workflow: get_workflow_task_by_template_id now returns a Task object List


## [v0.0.2-beta.1] - 2024-12-06

### Added

- Workflow: add base functionality for workflows
- People: add base functionality for people
- core: automatically get api user person object (optional, default: True)

## [v0.0.2-beta.0] - 2024-12-05

### Added

- Request: add methods: archive, trash, restore

### Bug Fixes

- Request: Fix get_request, get_notes method


## [v0.0.1] - 2024-12-05

### Added

- Pagination: auto pagination get requests
- Retry-after: auto retry after 429 status code
- custom fields conversion (from and to object/dict)
