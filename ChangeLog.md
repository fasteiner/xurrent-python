# Change Log

## v0.0.2.10

### New Features

- Core: add enum LogLevel
- Core: add method set_log_level to change the log level

### Breaking Changes

- Core: init: parameter for logger has been added, if not provided, a new logger will be created

## v0.0.2.9

### New Features

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

### Bugfixes

- Person, Workflow, Task: inherit JsonSerializableDict --> make serializable
- Request: close: make it possible to close a without a note (using default note)

### Breaking Changes

- Request: request.created_by, request.requested_by, request.requested_for, request.member are now Person objects
- Workflow: workflow.manager is now a Person object

## v0.0.2.8

### Bug Fixes

- Core: __append_per_page: exclude auto append for /me

### Breaking Changes

- Request: request.workflow is now a Workflow object instead of a dict --> request.workflow.id instead of request.workflow['id']

## v0.0.2.7

### Bug Fixes

- Task: `__update_object__` fixed

## v0.0.2.6

### Bug Fixes

- Task: Fix update method

## v0.0.2.5

### Bug Fixes

- Task: Fix update method

## v0.0.2.4

### New Features

- People: add non static methods: enable, archive, trash, restore
- People: add static methods: create, get_people
- Workflows: add static methods: get_workflows

## v0.0.2.3

### New Features

- Task: add non static methods: get_workflow, close, approve, reject, cancel, create
- Workflow: add non static methods: create_task

## v0.0.2.2

### New Features

- Task: add base functionality for tasks
- Workflow: add methods: get_task_by_template_id, get_tasks
- Workflow: update: add check for possible status values
- Request: add static method: update_by_id

### Bug Fixes

- Workflow: Fix toString / __str__ method

### Breaking Changes

- Request: renamed get_request to get_requests
- Workflow: get_workflow_task_by_template_id now returns a Task object List


## v0.0.2.1

### New Features

- Workflow: add base functionality for workflows
- People: add base functionality for people
- core: automatically get api user person object (optional, default: True)

## v0.0.2

### New Features

- Request: add methods: archive, trash, restore

### Bug Fixes

- Request: Fix get_request, get_notes method


## v0.0.1

### New Features

- Pagination: auto pagination get requests
- Retry-after: auto retry after 429 status code
- custom fields conversion (from and to object/dict)