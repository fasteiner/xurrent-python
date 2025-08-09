# Xurrent Module

[![PyPI version](https://img.shields.io/pypi/v/xurrent)](https://pypi.org/project/xurrent/)
[![Downloads](https://img.shields.io/pypi/dm/xurrent)](https://pypistats.org/packages/xurrent)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


This module is used to interact with the Xurrent API. It provides a set of classes to interact with the API.

## Change Log

[ChangeLog.md](https://github.com/fasteiner/xurrent-python/blob/main/CHANGELOG.md)

## Contributing

[Contributing.md](Contributing.md)

## Usage

### Basic Usage

```python
    from xurrent.core import XurrentApiHelper

    apitoken = "********"

    baseUrl = "https://api.xurrent.qa/v1"
    account = "account-name"

    x_api_helper = XurrentApiHelper(baseUrl, apitoken, account)

    # change log level (default: INFO)
    x_api_helper.set_log_level("DEBUG")

    # Plain API Call
    uri = "/requests?subject=Example Subject"
    x_api_helper.api_call(uri, 'GET')

    # Convert node ID
    x_api_helper.decode_api_id('ZmFiaWFuc3RlaW5lci4yNDEyMTAxMDE0MTJANG1lLWRlbW8uY29tL1JlcS83MDU3NTU') # fabiansteiner.241210101412@4me-demo.com/Req/705755
    # this can be used to derive the ID from the nodeID
```

#### Configuration Items

```python
    # Example usage of ConfigurationItem class
    from xurrent.configuration_items import ConfigurationItem
    
    # Get a Configuration Item by ID
    ci = ConfigurationItem.get_by_id(x_api_helper, <id>)
    print(ci)

    # List all Configuration Items
    all_cis = ConfigurationItem.get_configuration_items(x_api_helper)
    print(all_cis)

    # List active Configuration Items
    active_cis = ConfigurationItem.get_configuration_items(x_api_helper, predefinedFilter="active")
    print(active_cis)

    # Update a Configuration Item
    updated_ci = ci.update({"name": "Updated Name", "status": "being_repaired"})
    print(updated_ci)

    # Create a new Configuration Item
    # creating without specifying the label, takes the last ci of the product and increments the label
    # example: "wdc-02" -> "wdc-03"
    data = {"name": "New CI", "type": "software", "status": "in_production", "product_id": "<product_id>"}
    new_ci = ConfigurationItem.create(x_api_helper, data)
    print(new_ci)

    # Archive a Configuration Item (must be in an allowed state)
    try:
        archived_ci = ci.archive()
        print(archived_ci)
    except ValueError as e:
        print(f"Error: {e}")

    # Trash a Configuration Item (must be in an allowed state)
    try:
        trashed_ci = ci.trash()
        print(trashed_ci)
    except ValueError as e:
        print(f"Error: {e}")

    # Restore a Configuration Item
    restored_ci = ci.restore()
    print(restored_ci)
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

##### Request Configuration Items

```python
    from src.xurrent.requests import Request

    # Get Configuration Items for a Request
    request_id = <request_id>


    # Add a Configuration Item to a Request
    ci_id = <ci_id>
    try:
        response = Request.add_ci_to_request_by_id(x_api_helper, request_id, ci_id)
        print("CI added:", response)
    except ValueError as e:
        print(f"Error: {e}")

    cis = Request.get_cis_by_request_id(x_api_helper, request_id)
    print(cis)

    # Remove a Configuration Item from a Request
    try:
        response = Request.remove_ci_from_request_by_id(x_api_helper, request_id, ci_id)
        print("CI removed:", response)
    except ValueError as e:
        print(f"Error: {e}")

    # Instance-based example
    req = Request.get_by_id(x_api_helper, request_id)

    # Add a CI to this request
    try:
        response = req.add_ci(ci_id)
        print("CI added:", response)
    except ValueError as e:
        print(f"Error: {e}")

    # Get CIs for this request
    cis_instance = req.get_cis()
    print(cis_instance)

    # Remove a CI from this request
    try:
        response = req.remove_ci(ci_id)
        print("CI removed:", response)
    except ValueError as e:
        print(f"Error: {e}")
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

### Bulk Export
```python
    import csv
    import io

    #Request a bulk export of "people"
    csvdata = x_api_helper.bulk_export("people")

    #Iterate fetched export rows with the csv library, where row 1 defines the column names
    for row in csv.DictReader(io.StringIO(csvdata)):
        print(row["Employee Number"])
```
