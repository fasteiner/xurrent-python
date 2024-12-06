# Change Log

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