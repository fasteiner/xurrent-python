from .core import XurrentApiHelper, JsonSerializableDict
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

class TaskStatus(str, Enum):
    registered = "registered"  # Registered
    declined = "declined"  # Declined
    assigned = "assigned"  # Assigned
    accepted = "accepted"  # Accepted
    in_progress = "in_progress"  # In Progress
    waiting_for = "waiting_for"  # Waiting for…
    waiting_for_customer = "waiting_for_customer"  # Waiting for Customer
    request_pending = "request_pending"  # Request Pending
    failed = "failed"  # Failed
    rejected = "rejected"  # Rejected
    completed = "completed"  # Completed
    approved = "approved"  # Approved
    canceled = "canceled"  # Canceled


class Task(JsonSerializableDict):
    #https://developer.xurrent.com/v1/tasks/
    __resourceUrl__ = 'tasks'

    def __init__(self, connection_object: XurrentApiHelper, id, subject: str = None, workflow: dict = None,description: str = None, **kwargs):
        self._connection_object = connection_object
        self.id = id
        self.subject = subject
        self.workflow = workflow
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        """
        Return a string representation of the object.
        """
        return f"Task(id={self.id}, subject={self.subject}, workflow={self.workflow})"

    def ref_str(self) -> str:
        """
        Return a string representation of the object.
        """
        return f"Task(id={self.id}, subject={self.subject})"
    
    @classmethod
    def from_data(cls, connection_object: XurrentApiHelper, data) -> T:
        if not isinstance(data, dict):
            raise TypeError(f"Expected 'data' to be a dictionary, got {type(data).__name__}")
        if 'id' not in data:
            raise ValueError("Data dictionary must contain an 'id' field.")
        return cls(connection_object, **data)

    @classmethod
    def get_by_id(cls, connection_object: XurrentApiHelper, id) -> T:
        uri = f'{connection_object.base_url}/{Task.__resourceUrl__}/{id}'
        return cls.from_data(connection_object, connection_object.api_call(uri, 'GET'))

    @classmethod
    def get_tasks(cls, connection_object: XurrentApiHelper, predefinedFilter: TaskPredefinedFilter = None, queryfilter: dict = None) -> List[T]:
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        if predefinedFilter:
            uri = f'{uri}/{predefinedFilter}'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        return connection_object.api_call(uri, 'GET')

    @staticmethod
    def get_workflow_of_task(connection_object: XurrentApiHelper, id, expand: bool = False) -> Workflow:
        task = Task.get_by_id(connection_object, id)
        if expand:
            return Workflow.get_by_id(connection_object, task.workflow.id)
        return Workflow.from_data(connection_object, task.workflow)

    def get_workflow(self, expand: bool = False) -> Workflow:
        if task.workflow and not expand:
            return Workflow.from_data(self._connection_object, self.workflow)
        elif task.workflow and expand:
            return Workflow.get_by_id(self._connection_object, self.workflow.id)
        elif not task.workflow:
            return Task.get_workflow_of_task(self._connection_object, self.id, expand)


    @staticmethod
    def update_by_id(connection_object: XurrentApiHelper, id, data) -> T:
        task = Task(connection_object=connection_object, id=id)
        return task.update(data)

    def update(self, data) -> T:
        uri = f'{self._connection_object.base_url}/{Task.__resourceUrl__}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        return Task.from_data(self._connection_object,response)

    def close(self, note: str = None, member_id: int = None) -> T:
        """
        Close the task.

        :param note: Note to add to the task
        :param member_id: ID of the member who should close the task
        """
        if(self.category == "approval"):
            raise ValueError("Approval tasks cannot be closed. Use the 'approve' or 'reject' method instead.")
        return self.update({
            'status': 'completed',
            'note': note or "Task closed by API user",
            'member_id': member_id or self._connection_object.api_user.id
        })

    def approve(self, note: str = None, member_id: int = None) -> T:
        """
        Approve the task.

        :param note: Note to add to the task
        :param member_id: ID of the member who should approve the task
        """
        if(self.category != "approval"):
            raise ValueError("Only approval tasks can be approved.")
        return self.update({
            'status': 'approved',
            'note': note or "Task approved by API user",
            'member_id': member_id or self._connection_object.api_user.id
        })
    
    def reject(self, note: str = None, member_id: int = None) -> T:
        """
        Reject the task.

        :param note: Note to add to the task
        :param member_id: ID of the member who should reject the task
        """

        if(self.category != "approval"):
            raise ValueError("Only approval tasks can be rejected.")
        return self.update({
            'status': 'rejected',
            'note': note or "Task rejected by API user",
            'member_id': member_id or self._connection_object.api_user.id
        })

    def cancel(self, note: str = None, member_id: int = None) -> T:
        """
        Cancel the task.

        :param note: Note to add to the task
        :param member_id: ID of the member who should cancel the task
        """
        return self.update({
            'status': 'canceled',
            'note': note or "Task canceled by API user",
            'member_id': member_id or self._connection_object.api_user.id
        })
    
    @classmethod
    def create(cls, connection_object: XurrentApiHelper, workflowID: int,data: dict) -> T:
        """
        Create a new task.

        :param workflowID: ID of the workflow to create the task in
        :param data: Data to create the task with
        """
        uri = f'{connection_object.base_url}/workflows/{workflowID}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)
