# Xurrent Module

This module is used to interact with the Xurrent API. It provides a set of classes to interact with the API.


## Usage

```python
    from xurrent.core import XurrentApiHelper
    from xurrent.requests import Request
    from xurrent.tasks import Task

    apitoken = "********"

    baseUrl = "https://api.4me.qa/v1"
    account = "tttech-it"

    logger = setup_logger(verbose=True)

    x_api_helper = XurrentApiHelper(baseUrl, apitoken, account)

    request = Request.get_by_id(x_api_helper, 10158378)
    task = Task.get_by_id(x_api_helper, 5986404)

```
