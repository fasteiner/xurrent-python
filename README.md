# Xurrent Module

This module is used to interact with the Xurrent API. It provides a set of classes to interact with the API.

## Change Log

[ChangeLog.md](https://github.com/fasteiner/xurrent-python/blob/main/ChangeLog.md)

## Contributing

[Contributing.md](Contributing.md)

## Usage

### Basic Usage

```python
    from xurrent.core import XurrentApiHelper

    apitoken = "********"

    baseUrl = "https://api.4me.qa/v1"
    account = "account-name"

    x_api_helper = XurrentApiHelper(baseUrl, apitoken, account)

    # change log level (default: INFO)
    x_api_helper.set_log_level("DEBUG")

    # Plain API Call
    uri = "/requests?subject=Example Subject"
    connection_object.api_call(uri, 'GET')

    # Convert node ID
    helper.decode_api_id('ZmFiaWFuc3RlaW5lci4yNDEyMTAxMDE0MTJANG1lLWRlbW8uY29tL1JlcS83MDU3NTU') # fabiansteiner.241210101412@4me-demo.com/Req/705755
    # this can be used to derive the ID from the nodeID

```

#### People

```python
    from xurrent.people import Person

    people = Person.get_by_id(x_api_helper, <id>)

    api_user = Person.get_me(x_api_helper)

    # get all people with a specific subject
    people = Person.get_people(x_api_helper,queryfilter={
    "name": "Werner"
    })

    # enable
    people.enable()

    #disable
    people.disable()
    #archive
    people.archive()
    #trash
    people.trash()
    #restore
    people.restore()

```

#### Requests

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

##### Request Notes

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

#### Tasks

```python
    from xurrent.tasks import Task

    task = Task.get_by_id(x_api_helper, <id>)

    # get all tasks with a specific subject
    tasks = Task.get_task(x_api_helper,queryfilter={
    "subject": "Example Subject"
    })

    # get workflow of task (use expand: True to get the full workflow object)
    workflow = task.get_workflow(expand=True)
    # or statically
    workflow = Task.get_workflow_by_template_id(x_api_helper, <id>, expand=True)

    # close
    task.close()
    #cancel
    task.cancel() # only possible before the task is started
    #reject
    task.reject()
    #approve
    task.approve()


```

#### Teams

```python
    from xurrent.teams import Team

    team = Team.get_by_id(x_api_helper, <id>)

    # get all teams with a specific subject
    teams = Team.get_team(x_api_helper,predifinedFilter="enabled")

    # enable
    team.enable()

    #disable
    team.disable()
    #archive
    team.archive()
    #trash
    team.trash()
    #restore
    team.restore()

```

#### Workflows

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
