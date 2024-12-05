from .core import XurrentApiHelper
from .core import JsonSerializableDict
from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Type, TypeVar

class CompletionReason(str, Enum):
    solved = "solved"  # Solved - Root Cause Analysis Not Required
    workaround = "workaround"  # Workaround - Root Cause Not Removed
    gone = "gone"  # Gone - Unable to Reproduce
    duplicate = "duplicate"  # Duplicate - Same as Another Request of Customer
    withdrawn = "withdrawn"  # Withdrawn - Withdrawn by Requester
    no_reply = "no_reply"  # No Reply - No Reply Received from Customer
    rejected = "rejected"  # Rejected - Rejected by Approver
    conflict = "conflict"  # Conflict - In Conflict with Internal Standard or Policy
    declined = "declined"  # Declined - Declined by Service Provider
    unsolvable = "unsolvable"  # Unsolvable - Unable to Solve


class PredefinedFilter(str, Enum):
    completed = "completed"  # /requests/completed
    open = "open"  # /requests/open
    requested_by_or_for_me = "requested_by_or_for_me"  # /requests/requested_by_or_for_me
    assigned_to_my_team = "assigned_to_my_team"  # /requests/assigned_to_my_team
    assigned_to_me = "assigned_to_me"  # /requests/assigned_to_me
    waiting_for_me = "waiting_for_me"  # /requests/waiting_for_me
    problem_management_review = "problem_management_review"  # /requests/problem_management_review
    sla_accountability = "sla_accountability"  # /requests/sla_accountability


T = TypeVar("T", bound="Request")  # Define the type variable

class Request(JsonSerializableDict):
    #https://developer.4me.com/v1/requests/
    resourceUrl = 'requests'

    def __init__(self,
                 connection_object: XurrentApiHelper,
                 id: int,
                 source: Optional[str] = None,
                 sourceID: Optional[str] = None,
                 subject: Optional[str] = None,
                 category: Optional[str] = None,
                 impact: Optional[str] = None,
                 status: Optional[str] = None,
                 next_target_at: Optional[datetime] = None,
                 completed_at: Optional[datetime] = None,
                 team: Optional[Dict[str, str]] = None,
                 member: Optional[Dict[str, str]] = None,
                 grouped_into: Optional[int] = None,
                 service_instance: Optional[Dict[str, str]] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object  # Private attribute for connection object
        self.source = source
        self.sourceID = sourceID
        self.subject = subject
        self.category = category
        self.impact = impact
        self.status = status
        self.next_target_at = next_target_at
        self.completed_at = completed_at
        self.team = team
        self.member = member
        self.grouped_into = grouped_into
        self.service_instance = service_instance
        self.created_at = created_at
        self.updated_at = updated_at
        # Initialize any additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __update_object__(self, data) -> None:
        if data.get('id') != self.id:
            raise ValueError(f"ID mismatch: {self.id} != {data.get('id')}")
        for key, value in data.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        """Provide a human-readable string representation of the object."""
        return (f"Request(id={self.id}, subject={self.subject}, category={self.category}, "
                f"status={self.status}, impact={self.impact})")

    @classmethod
    def from_data(cls, connection_object: XurrentApiHelper, data) -> T:
        if not isinstance(data, dict):
            raise TypeError(f"Expected 'data' to be a dictionary, got {type(data).__name__}")
        if not 'id' in data:
            data['id'] = id
        return cls(connection_object, **data)



    @classmethod
    def get_by_id(cls, connection_object: XurrentApiHelper, id: int) -> T:
        """
        Retrieve a request by its ID and return it as an instance of Request.
        :param connection_object: Instance of XurrentApiHelper
        :param id: ID of the request to retrieve
        :return: Instance of Request
        """
        uri = f'{connection_object.base_url}/{cls.resourceUrl}/{id}'
        response = connection_object.api_call(uri, 'GET')
        return cls.from_data(connection_object, response)

    @classmethod
    def get_request(cls, connection_object: XurrentApiHelper, predefinedFiler: PredefinedFilter = None,filter: dict = None) -> List[T]:
        """
        Retrieve a request by its ID.
        :param connection_object: Instance of XurrentApiHelper
        :param id: ID of the request to retrieve
        :return: Request data
        """
        uri = f'{connection_object.base_url}/{cls.resourceUrl}'
        if predefinedFiler:
            uri += f'/{predefinedFiler}'
        if filter:
            uri += '?' + connection_object.create_filter_string(filter)
        response = connection_object.api_call(uri, 'GET')
        return [cls.from_data(connection_object, item) for item in response]

    @staticmethod
    def add_note_to_request(connection_object: XurrentApiHelper, id: int, note) -> dict:
        """
        Add a note to a request by its ID.
        :param connection_object: Instance of XurrentApiHelper
        :param id: ID of the request
        :param note: Dictionary containing the note data
        :return: Response from the API call
        """
        uri = f'{connection_object.base_url}/{Request.resourceUrl}/{id}/notes'
        return connection_object.api_call(uri, 'POST', note)

    def add_note_to_request(self, note: dict) -> dict:
        """
        Add a note to the current request instance.
        :param note: Dictionary containing the note data
        :return: Response from the API call (the note that was added)
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to add a note.")
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}/notes'
        return self._connection_object.api_call(uri, 'POST', note)

    def get_notes(self, filter : dict = None) -> List[dict]:
        """
        Retrieve all notes associated with the current request instance.
        :return: List of notes
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to get notes.")
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}/notes'
        if filter:
            uri += '?' + self._connection_object.create_filter_string(filter)
        return self._connection_object.api_call(uri, 'GET')

    def get_note_by_id(self, note_id) -> dict:
        """
        Retrieve a note by its ID associated with the current request instance.
        :param note_id: ID of the note to retrieve
        :return: Note data
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to get notes.")
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}/notes/{note_id}'
        return self._connection_object.api_call(uri, 'GET')

    @staticmethod
    def get_notes(connection_object: XurrentApiHelper, request_id, note_id):
        if not request_id:
            raise ValueError("Must pass a request ID to get notes.")
        uri = f'{connection_object.base_url}/{Request.resourceUrl}/{request_id}/notes/{note_id}'
        return connection_object.api_call(uri, 'GET')

    @classmethod
    def update(cls : Type[T], connection_object: XurrentApiHelper, id, data) -> T:
        uri = f'{connection_object.base_url}/{cls.resourceUrl}/{id}'
        response = connection_object.api_call(uri, 'PATCH', data)
        return cls.from_data(connection_object, response)

    def update(self, data: dict):
        """
        Update the current request instance with new data.
        :param data: Dictionary containing updated data
        :return: Response from the API call
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to update.")
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        self.__update_object__(response)
        return self

    def close(self, note: str, completion_reason: CompletionReason = CompletionReason.solved):
        """
        Close the current request instance.
        :return: Response from the API call
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to close.")
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}'
        response = self._connection_object.api_call(uri, 'POST', {'status': 'completed', 'completion_reason': completion_reason, 'note': note})
        self.__update_object__(response)
        return self

    def close_and_trash(self):
        """
        Close and trash the current request instance.
        :return: Response from the API call
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to close and trash.")
        self.close()
        return self.trash()

    def trash(self, force=False):
        """
        Trashes the current request instance.

        :param force: Whether to force the trash operation (if force: the request will be closed and trashed)
        :return: Response from the API call
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to trash.")
        uri = f'{self._connection_object.base_url}/{self.resourceUrl}/{self.id}/trash'
        try:
            response = self._connection_object.api_call(uri, 'POST')
            self.__update_object__(response)
            return self
        except Exception as e:
            if force:
                return self.close_and_trash()
            else:
                raise e

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict):
        """
        Create a new request and return it as an instance of Request.
        :param connection_object: Instance of XurrentApiHelper
        :param data: Dictionary containing request data
        :return: Instance of Request
        """
        uri = f'{connection_object.base_url}/{cls.resourceUrl}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)
