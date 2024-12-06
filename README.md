# Xurrent Module

This module is used to interact with the Xurrent API. It provides a set of classes to interact with the API.

## Change Log

[ChangeLog.md](https://github.com/fasteiner/xurrent-python/blob/main/ChangeLog.md)

## Usage

### Basic Usage

```python
    from xurrent.core import XurrentApiHelper

    apitoken = "********"

    baseUrl = "https://api.4me.qa/v1"
    account = "account-name"

    logger = setup_logger(verbose=True)

    x_api_helper = XurrentApiHelper(baseUrl, apitoken, account)

    # Plain API Call
    uri = "/requests?subject=Example Subject"
    connection_object.api_call(uri, 'GET')

```

### Requests
```python
    from xurrent.requests import Request

    request = Request.get_by_id(x_api_helper, <id>)

    # get all requests with a specific subject
    requests = Request.get_request(x_api_helper,queryfilter={
    "subject": "Example Subject"
    })

    # close
    request.close("closed")

    # archive
    request.archive()

    #trash
    request.trash()

    #restore

    request.restore()
    

```

#### Request Notes

```python
    from xurrent.requests import Request
    
    request = Request.get_by_id(x_api_helper, <id>)

    request_note = request.get_by_id(x_api_helper, <id>)

    # get all request notes with a specific subject
    request_notes = request.get_notes(x_api_helper, predefinedFilter="public")

    request.add_note("This is a test note")
    request.add_note({
        "text": "This is a test note",
        "internal": True
    })

```

### Workflows

```python

    from xurrent.workflows import Workflow

    workflow = Workflow.get_by_id(x_api_helper, <id>)

    #close
    workflow.close() # completion reason: completed, note: closed
    # close with completion reason
    workflow.close(completion_reason="withdrawn")
    #close with completion reason and note
    workflow.close(completion_reason="withdrawn", note="This is a test note")

```

### Tasks

```python
    from xurrent.tasks import Task

    task = Task.get_by_id(x_api_helper, <id>)

    # get all tasks with a specific subject
    tasks = Task.get_task(x_api_helper,queryfilter={
    "subject": "Example Subject"
    })

```
