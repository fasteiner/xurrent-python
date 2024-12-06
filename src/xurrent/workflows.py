from datetime import datetime
from typing import Optional, List, Dict
from .core import XurrentApiHelper
from enum import Enum

class WorkflowCompletionReason(str, Enum):
    withdrawn = "withdrawn"  # Withdrawn - Withdrawn by Requester
    rejected = "rejected"    # Rejected - Rejected by Approver
    rolled_back = "rolled_back"  # Rolled Back - Original Environment Restored
    failed = "failed"        # Failed - No Requirements Met
    partial = "partial"      # Partial - Not All Requirements Met
    disruptive = "disruptive"  # Disruptive - Caused Service Disruption
    complete = "complete"    # Complete - All Requirements Met

class WorkflowStatus(str, Enum):
    being_created = "being_created"  # Being Created
    registered = "registered"        # Registered
    in_progress = "in_progress"      # In Progress
    progress_halted = "progress_halted"  # Progress Halted
    completed = "completed"          # Completed
    # risk_and_impact = "risk_and_impact"  # Risk & Impact — deprecated: replaced by in_progress
    # approval = "approval"            # Approval — deprecated: replaced by in_progress
    # implementation = "implementation"  # Implementation — deprecated: replaced by in_progress


class WorkflowPredefinedFilter(str, Enum):
    """
    Predefined filters for tasks.
    """
    open = 'open' # /workflows/completed: List all completed workflows
    completed = 'completed' #/workflows/open: List all open workflows
    managed_by_me = 'managed_by_me' #/workflows/managed_by_me: List all workflows which manager is the API user


class Workflow:
    # Endpoint for workflows
    resourceUrl = 'workflows'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 subject: Optional[str] = None,
                 status: Optional[str] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object
        self.subject = subject
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        """Provide a human-readable string representation of the object."""
        return (f"Workflow(id={self.id}, subject={self.subject}, status={self.status}, "
                f"category={self.category}, impact={self.impact})")

    @classmethod
    def from_data(cls, connection_object: XurrentApiHelper, data: dict):
        if not isinstance(data, dict):
            raise TypeError(f"Expected 'data' to be a dictionary, got {type(data).__name__}")
        if 'id' not in data:
            raise ValueError("Data dictionary must contain an 'id' field.")
        return cls(connection_object, **data)

    @classmethod
    def get_by_id(cls, connection_object: XurrentApiHelper, id: int) -> dict:
        """
        Retrieve a workflow by its ID.
        """
        uri = f'{connection_object.base_url}/{cls.resourceUrl}/{id}'
        return cls.from_data(connection_object, connection_object.api_call(uri, 'GET'))

    @classmethod
    def get_workflow_tasks_by_workflow_id(cls, connection_object: XurrentApiHelper, id: int) -> List[dict]:
        """
        Retrieve all tasks associated with a workflow by its ID.
        """
        uri = f'{connection_object.base_url}/{cls.resourceUrl}/{id}/tasks'
        return connection_object.api_call(uri, 'GET')

    @classmethod
    def get_workflow_task_by_template_id(cls, connection_object: XurrentApiHelper, workflowID: int, templateID: int) -> dict:
        """
        Retrieve a specific task associated with a workflow by template ID.
        """
        uri = f'{connection_object.base_url}/{cls.resourceUrl}/{workflowID}/tasks?template={templateID}'
        tasks = connection_object.api_call(uri, 'GET')
        if not tasks:
            return None
        if len(tasks) > 1:
            raise Exception(f"Multiple tasks found for templateID: {templateID}")
        return tasks[0]

    def update(self, data: dict):
        """
        Update the current workflow instance with new data.
        """
        if not self.id:
            raise ValueError("Workflow instance must have an ID to update.")
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        self.__update_object__(response)
        return self

    @staticmethod
    def update_by_id(connection_object: XurrentApiHelper, id: int, data: dict) -> dict:
        """
        Update a workflow by its ID.
        """
        workflow = Workflow(connection_object, id)
        return workflow.update(data)

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict):
        """
        Create a new workflow.
        """
        uri = f'{connection_object.base_url}/{cls.resourceUrl}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    def close(self, note="closed.", completion_reason=WorkflowCompletionReason.complete):
        """
        Close the current workflow instance.
        """
        if not self.id:
            raise ValueError("Workflow instance must have an ID to close.")
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', {
            'note': note,
            'manager_id': self._connection_object.api_user.id,
            'status': WorkflowStatus.completed,
            'completion_reason': completion_reason
            })
        self.__update_object__(response)
        return self

    def archive(self):
        """
        Archive the current workflow instance.
        """
        if not self.id:
            raise ValueError("Workflow instance must have an ID to archive.")
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}/archive'
        response = self._connection_object.api_call(uri, 'POST')
        self.__update_object__(response)
        return self

    def trash(self):
        """
        Trash the current workflow instance.
        """
        if not self.id:
            raise ValueError("Workflow instance must have an ID to trash.")
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}/trash'
        response = self._connection_object.api_call(uri, 'POST')
        self.__update_object__(response)
        return self

    def restore(self):
        """
        Restore the current workflow instance.
        """
        if not self.id:
            raise ValueError("Workflow instance must have an ID to restore.")
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}/restore'
        response = self._connection_object.api_call(uri, 'POST')
        self.__update_object__(response)
        return self

    def __update_object__(self, data):
        """
        Update the instance properties with new data.
        """
        if data.get('id') != self.id:
            raise ValueError(f"ID mismatch: {self.id} != {data.get('id')}")
        for key, value in data.items():
            setattr(self, key, value)
