# Xurrent Module

[![PyPI version](https://img.shields.io/pypi/v/xurrent)](https://pypi.org/project/xurrent/)
[![Downloads](https://img.shields.io/pypi/dm/xurrent)](https://pypistats.org/packages/xurrent)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


This module is used to interact with the [Xurrent API](https://developer.xurrent.com/v1/). It provides a class per
Xurrent resource (requests, tasks, workflows, people, CIs, ...) and handles authentication (API token or OAuth client
credentials), pagination and rate limits.

```bash
pip install xurrent
```

## Documentation

The [API reference](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/README.md) has a page per class
with its fields, enums, methods (with the API endpoint each one calls) and cross references to the other classes:

<!-- api-reference:start -->
| Class | API resource | Class | API resource |
|---|---|---|---|
| [Calendar](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Calendar.md) | `/calendars` | [Request](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Request.md) | `/requests` |
| [ClosureCode](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/ClosureCode.md) | `/closure_codes` | [RequestTemplate](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/RequestTemplate.md) | `/request_templates` |
| [ConfigurationItem](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/ConfigurationItem.md) | `/cis` | [Risk](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Risk.md) | `/risks` |
| [Contract](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Contract.md) | `/contracts` | [Service](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Service.md) | `/services` |
| [CustomCollection](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/CustomCollection.md) | `/custom_collections` | [ServiceInstance](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/ServiceInstance.md) | `/service_instances` |
| [CustomCollectionElement](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/CustomCollectionElement.md) | `/custom_collection_elements` | [ServiceOffering](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/ServiceOffering.md) | `/service_offerings` |
| [EffortClass](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/EffortClass.md) | `/effort_classes` | [ShopArticle](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/ShopArticle.md) | `/shop_articles` |
| [Holiday](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Holiday.md) | `/holidays` | [ShopArticleCategory](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/ShopArticleCategory.md) | `/shop_article_categories` |
| [KnowledgeArticle](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/KnowledgeArticle.md) | `/knowledge_articles` | [ShopOrderLine](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/ShopOrderLine.md) | `/shop_order_lines` |
| [Organization](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Organization.md) | `/organizations` | [Site](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Site.md) | `/sites` |
| [OutOfOfficePeriod](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/OutOfOfficePeriod.md) | `/out_of_office_periods` | [SkillPool](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/SkillPool.md) | `/skill_pools` |
| [Person](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Person.md) | `/people` | [Task](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Task.md) | `/tasks` |
| [Problem](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Problem.md) | `/problems` | [Team](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Team.md) | `/teams` |
| [Product](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Product.md) | `/products` | [TimeAllocation](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/TimeAllocation.md) | `/time_allocations` |
| [ProductCategory](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/ProductCategory.md) | `/product_categories` | [UiExtension](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/UiExtension.md) | `/ui_extensions` |
| [Project](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Project.md) | `/projects` | [Workflow](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Workflow.md) | `/workflows` |
| [ProjectTask](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/ProjectTask.md) | `/project_tasks` | [WorkflowTemplate](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/WorkflowTemplate.md) | `/workflow_templates` |
| [Release](https://github.com/fasteiner/xurrent-python/blob/main/docs/api/Release.md) | `/releases` | | |
<!-- api-reference:end -->

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

#### Using OAuth client credentials

You can let the helper automatically request and refresh bearer tokens by providing the OAuth
`client_id` and `client_secret` that were issued to your application. The original API key flow
continues to work unchanged, but only one authentication method may be used per helper instance.

```python
    from xurrent.core import XurrentApiHelper

    baseUrl = "https://api.xurrent.qa/v1"
    account = "account-name"
    client_id = "your-client-id"
    client_secret = "your-client-secret"

    x_api_helper = XurrentApiHelper(
        baseUrl,
        api_account=account,
        client_id=client_id,
        client_secret=client_secret,
    )

    response = x_api_helper.api_call("/requests", "GET")
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
    data = {"name": "New CI", "status": "in_production", "product_id": "<product_id>"}
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

    person = Person.get_by_id(x_api_helper, <id>)

    api_user = Person.get_me(x_api_helper)

    # get all people with a specific name
    people = Person.get_people(x_api_helper, queryfilter={
        "name": "Werner"
    })

    # enable
    person.enable()

    #disable
    person.disable()
    #archive
    person.archive()
    #trash
    person.trash()
    #restore
    person.restore()
```

#### Requests

```python
    from xurrent.requests import Request

    request = Request.get_by_id(x_api_helper, <id>)

    # get all requests with a specific subject
    requests = Request.get_requests(x_api_helper, queryfilter={
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
    from xurrent.requests import Request

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
    
    from xurrent.requests import PredefinedNotesFilter

    request = Request.get_by_id(x_api_helper, <id>)

    # a note of the request by its ID
    request_note = request.get_note_by_id(<note_id>)

    # all public notes of the request
    request_notes = request.get_notes(predefinedFilter=PredefinedNotesFilter.public)

    # only the newest note (one API call with per_page=1); the same for tasks, problems, project tasks, ...
    newest = request.get_notes(sort="-created_at", max_results=1)

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
    tasks = Task.get_tasks(x_api_helper, queryfilter={
        "subject": "Example Subject"
    })

    # get workflow of task (use expand=True to read the full workflow from the API)
    workflow = task.get_workflow(expand=True)
    # or statically, by the ID of the task
    workflow = Task.get_workflow_of_task(x_api_helper, <task_id>, expand=True)

    # close
    task.close()
    #cancel
    task.cancel() # only possible before the task is started
    #reject
    task.reject()
    #approve
    task.approve()
```

#### Project Tasks

```python
    from xurrent.project_tasks import ProjectTask, ProjectTaskPredefinedFilter

    project_task = ProjectTask.get_by_id(x_api_helper, <id>)

    # get the project tasks assigned to the API user (at most 50)
    project_tasks = ProjectTask.get_project_tasks(x_api_helper, predefinedFilter=ProjectTaskPredefinedFilter.assigned_to_me, max_results=50)

    # notes
    notes = project_task.get_notes()
    project_task.add_note("This is a test note")
    project_task.add_note({"text": "This is a test note", "suppress_note_added_notifications": True})
```

#### Teams

```python
    from xurrent.teams import Team, TeamPredefinedFilter

    team = Team.get_by_id(x_api_helper, <id>)

    # get all enabled teams
    teams = Team.get_teams(x_api_helper, predefinedFilter=TeamPredefinedFilter.enabled)

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
    workflow.close() # completion reason: complete, note: "closed."
    # close with completion reason
    workflow.close(completion_reason="withdrawn")
    #close with completion reason and note
    workflow.close(completion_reason="withdrawn", note="This is a test note")

```

### Limiting results

List calls follow the pagination of the API and return all records by default. Pass
`max_results` to stop after that many records:

```python
    from xurrent.requests import Request

    # at most 25 requests assigned to the API user
    requests = Request.get_requests(x_api_helper, predefinedFiler="assigned_to_me", max_results=25)

    # at most 10 knowledge articles matching a full-text search, sorted by relevance
    results = x_api_helper.search("printer", types=["knowledge-article"], max_results=10)

    # plain API call
    x_api_helper.api_call("/requests/open", "GET", max_results=100)
```

### Bulk Export
```python
    import csv
    import io

    #Request a bulk export of "people" (returns the file as bytes)
    csvdata = x_api_helper.bulk_export("people").decode("utf-8-sig")

    #Iterate fetched export rows with the csv library, where row 1 defines the column names
    for row in csv.DictReader(io.StringIO(csvdata)):
        print(row["Employee Number"])
```
