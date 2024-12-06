from .core import XurrentApiHelper
from .workflows import Workflow
from enum import Enum
from typing import Optional, List, Dict, Type, TypeVar


T = TypeVar('T', bound='Task')

class TaskPredefinedFilter(str, Enum):
    finished = "finished"  # List all finished tasks
    open = "open"  # List all open tasks
    managed_by_me = "managed_by_me"  # List all tasks that are part of a workflow which manager is the API user
    assigned_to_my_team = "assigned_to_my_team"  # List all tasks that are assigned to one of the teams that the API user is a member of
    assigned_to_me = "assigned_to_me"  # List all tasks that are assigned to the API user
    approval_by_me = "approval_by_me"  # List all approval tasks that are assigned to the API user and which status is different from ‘Registered’





class Task():
    #https://developer.4me.com/v1/tasks/
    resourceUrl = 'tasks'

    def __init__(self, connection_object: XurrentApiHelper, id, subject: str = None, workflow: dict = None,description: str = None, **kwargs):
        self._connection_object = connection_object
        self.id = id
        self.subject = subject
        self.workflow = workflow
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __update_object__(self, data) -> None:
        if data.get('id') != self.id:
            raise ValueError(f"ID mismatch: {self.id} != {data.get('id')}")
        for key, value in data.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        """
        Return a string representation of the object.
        """
        return f"Task(id={self.id}, subject={self.subject}, workflow={self.workflow})"
    
    @classmethod
    def from_data(cls, connection_object: XurrentApiHelper, data) -> T:
        if not isinstance(data, dict):
            raise TypeError(f"Expected 'data' to be a dictionary, got {type(data).__name__}")
        if 'id' not in data:
            raise ValueError("Data dictionary must contain an 'id' field.")
        return cls(connection_object, **data)

    @classmethod
    def get_by_id(cls, connection_object: XurrentApiHelper, id) -> T:
        uri = f'{connection_object.base_url}/{Task.resourceUrl}/{id}'
        return cls.from_data(connection_object, connection_object.api_call(uri, 'GET'))

    @classmethod
    def get_tasks(cls, connection_object: XurrentApiHelper, predefinedFilter: TaskPredefinedFilter = None, queryfilter: dict = None) -> List[T]:
        uri = f'{connection_object.base_url}/{cls.resourceUrl}'
        if predefinedFilter:
            uri = f'{uri}/{predefinedFilter}'
        if queryfilter:
            uri = f'{uri}?{queryfilter}'
        return connection_object.api_call(uri, 'GET')

    @staticmethod
    def get_workflow_of_task(connection_object: XurrentApiHelper, id, expand: bool = False) -> Workflow:
        task = Task.get_by_id(connection_object, id)
        if expand:
            return Workflow.get_by_id(connection_object, task.workflow.id)
        return Workflow.from_data(connection_object, task.workflow)

    @staticmethod
    def update_by_id(connection_object: XurrentApiHelper, id, data) -> T:
        task = Task(connection_object=connection_object, id=id)
        return task.update(data)

    def update(self, data) -> T:
        uri = f'{connection_object.base_url}/{Task.resourceUrl}/{id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        self.__update_object__(response)
        return self
