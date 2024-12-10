# Change Log

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