from __future__ import annotations  # Needed for forward references
from .core import XurrentApiHelper, JsonSerializableDict
from .people import Person
from .teams import Team
from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Type, TypeVar

class RequestCategory(str, Enum):
    incident = "incident"  # Incident - Request for Incident Resolution
    rfc = "rfc"  # RFC - Request for Change
    rfi = "rfi"  # RFI - Request for Information
    reservation = "reservation"  # Reservation - Request for Reservation
    order = "order"  # Order - Request for Purchase
    fulfillment = "fulfillment"  # Fulfillment - Request for Order Fulfillment
    complaint = "complaint"  # Complaint - Request for Support Improvement
    compliment = "compliment"  # Compliment - Request for Bestowal of Praise
    other = "other"  # Other - Request is Out of Scope

    def __str__(self):
        return self.value

class RequestStatus(str, Enum):
    declined = "declined"  # Declined
    on_backlog = "on_backlog"  # On Backlog
    assigned = "assigned"  # Assigned
    accepted = "accepted"  # Accepted
    in_progress = "in_progress"  # In Progress
    waiting_for = "waiting_for"  # Waiting for…
    waiting_for_customer = "waiting_for_customer"  # Waiting for Customer
    reservation_pending = "reservation_pending"  # Reservation Pending
    workflow_pending = "workflow_pending"  # Workflow Pending
    project_pending = "project_pending"  # Project Pending
    completed = "completed"  # Completed

    def __str__(self):
        return self.value

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

    def __str__(self):
        return self.value


class PredefinedFilter(str, Enum):
    completed = "completed"  # /requests/completed
    open = "open"  # /requests/open
    requested_by_or_for_me = "requested_by_or_for_me"  # /requests/requested_by_or_for_me
    assigned_to_my_team = "assigned_to_my_team"  # /requests/assigned_to_my_team
    assigned_to_me = "assigned_to_me"  # /requests/assigned_to_me
    waiting_for_me = "waiting_for_me"  # /requests/waiting_for_me
    problem_management_review = "problem_management_review"  # /requests/problem_management_review
    sla_accountability = "sla_accountability"  # /requests/sla_accountability

    def __str__(self):
        return self.value

class PredefinedNotesFilter(str, Enum):
    public = "public"  # /requests/public
    internal = "internal"  # /requests/internal


T = TypeVar("T", bound="Request")  # Define the type variable


class Request(JsonSerializableDict):
    #https://developer.xurrent.com/v1/requests/
    __resourceUrl__ = 'requests'
    __references__ = ['workflow', 'requested_by', 'requested_for', 'created_by', 'member', 'team']
    workflow: Optional[Workflow]
    requested_by: Optional[Person]
    requested_for: Optional[Person]
    created_by: Optional[Person]
    category: Optional[RequestCategory]
    status: Optional[RequestStatus]
    team: Optional[Team]

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
                 member: Optional[Person] = None,
                 grouped_into: Optional[int] = None,
                 service_instance: Optional[Dict[str, str]] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 workflow: Optional[Workflow] = None,
                 requested_by: Optional[Person] = None,
                 requested_for: Optional[Person] = None,
                 created_by: Optional[Person] = None,
                 **kwargs):
        self.id = id
        self._connection_object = connection_object  # Private attribute for connection object
        self.source = source
        self.sourceID = sourceID
        self.subject = subject
        self.category = RequestCategory(category) if isinstance(category, str) else category if category else None
        self.impact = impact
        self.status = status
        self.next_target_at = next_target_at
        self.completed_at = completed_at
        self.team = team
        self.grouped_into = grouped_into
        self.service_instance = service_instance
        self.created_at = created_at
        self.updated_at = updated_at
        from .workflows import Workflow
        self.workflow = workflow if isinstance(workflow, Workflow) else Workflow.from_data(connection_object, workflow) if workflow else None
        from .people import Person
        self.member = member if isinstance(member, Person) else Person.from_data(connection_object, member) if member else None
        self.requested_by = requested_by if isinstance(requested_by, Person) else Person.from_data(connection_object, requested_by) if requested_by else None
        self.requested_for = requested_for if isinstance(requested_for, Person) else Person.from_data(connection_object, requested_for) if requested_for else None
        self.created_by = created_by if isinstance(created_by, Person) else Person.from_data(connection_object, created_by) if created_by else None
        self.team = team if isinstance(team, Team) else Team.from_data(connection_object, team) if team else None


        # Initialize any additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        """Provide a human-readable string representation of the object."""
        from .workflows import Workflow
        from .people import Person
        output: str = f"Request(id={self.id}, subject={self.subject}, category={self.category}, status={self.status}, impact={self.impact}"
        if(hasattr(self, 'created_by') and isinstance(self.created_by, Person)):
            output += f", created_by={self.created_by.ref_str()}"
        if(hasattr(self, 'workflow') and isinstance(self.workflow, Workflow)):
            output += f", workflow={self.workflow.ref_str()}"
        output += ")"
        return output

    def ref_str(self) -> str:
        """Provide a human-readable string representation of the object."""
        return f"Request(id={self.id}, subject={self.subject})"

    @classmethod
    def from_data(cls, connection_object: XurrentApiHelper, data) -> T:
        if not isinstance(data, dict):
            raise TypeError(f"Expected 'data' to be a dictionary, got {type(data).__name__}")
        if 'id' not in data:
            raise ValueError("Data dictionary must contain an 'id' field.")
        return cls(connection_object, **data)



    @classmethod
    def get_by_id(cls, connection_object: XurrentApiHelper, id: int) -> T:
        """
        Retrieve a request by its ID and return it as an instance of Request.
        :param connection_object: Instance of XurrentApiHelper
        :param id: ID of the request to retrieve
        :return: Instance of Request
        """
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}/{id}'
        response = connection_object.api_call(uri, 'GET')
        return cls.from_data(connection_object=connection_object, data=response)

    @classmethod
    def get_requests(cls, connection_object: XurrentApiHelper, predefinedFiler: PredefinedFilter = None,queryfilter: dict = None) -> List[T]:
        """
        Retrieve a request by its ID.
        :param connection_object: Instance of XurrentApiHelper
        :param id: ID of the request to retrieve
        :return: Request data
        """
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        if predefinedFiler:
            uri += f'/{predefinedFiler}'
        if queryfilter:
            uri += '?' + connection_object.create_filter_string(queryfilter)
        response = connection_object.api_call(uri, 'GET')
        return [cls.from_data(connection_object, item) for item in response]

    def add_note(self, note: dict) -> dict:
        """
        Add a note to the current request instance.
        :param note: Dictionary containing the note data
        :return: Response from the API call (the note that was added)
        """
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/notes'
        if(isinstance(note, dict)):
            return self._connection_object.api_call(uri, 'POST', note)
        elif(isinstance(note, str)):
            # this will post the note publically as the API User
            return self._connection_object.api_call(uri, 'POST', {'text': note})

    def get_notes(self, predefinedFilter: PredefinedNotesFilter=None, queryfilter : dict = None) -> List[dict]:
        """
        Retrieve all notes associated with the current request instance.
        :return: List of notes
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to get notes.")
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/notes'
        if predefinedFilter:
            uri += f'/{predefinedFilter}'
        if queryfilter:
            uri += '?' + self._connection_object.create_filter_string(queryfilter)
        return self._connection_object.api_call(uri, 'GET')

    def get_note_by_id(self, note_id) -> dict:
        """
        Retrieve a note by its ID associated with the current request instance.
        :param note_id: ID of the note to retrieve
        :return: Note data
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to get notes.")
        return self.get_notes(queryfilter={'id': note_id})[0]


    def update(self, data: dict):
        """
        Update the current request instance with new data.
        :param data: Dictionary containing updated data
        :return: Response from the API call
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to update.")
        # check if the category is valid
        if data.get('category') and not isinstance(data.get('category'), RequestCategory):
            data['category'] = RequestCategory(data.get('category'))
        # check if the status is valid
        if data.get('status') and not isinstance(data.get('status'), RequestStatus):
            data['status'] = RequestStatus(data.get('status'))

        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}'
        response = self._connection_object.api_call(uri, 'PATCH', data)
        return Request.from_data(self._connection_object,response)

    @staticmethod
    def update_by_id(connection_object: XurrentApiHelper, id: int, data: dict) -> T:
        """
        Update a request by its ID.
        :param connection_object: Instance of XurrentApiHelper
        :param id: ID of the request to update
        :param data: Dictionary containing updated data
        :return: Response from the API call
        """
        request = Request(connection_object, id)
        return request.update(data)

    def close(self, note: str = "Request closed over API.", completion_reason: CompletionReason = CompletionReason.solved, member_id: int = None, team_id: int = None):
        """
        Close the current request instance.
        :return: Response from the API call
        """
        if not member_id:
            member_id = self._connection_object.api_user.id
            if not member_id:
                raise ValueError("Member ID must be provided to close the request.")
        if not team_id:
            team_id = self._connection_object.api_user_teams[0].id
            if not team_id:
                raise ValueError("Team ID must be provided to close the request.")
        return self.update({'status': 'completed', 'completion_reason': completion_reason, 'note': note, "member_id": member_id, 'team_id': team_id})

    def close_and_trash(self, note: str = "Closing and trashing request", completion_reason: CompletionReason = CompletionReason.solved):
        """
        Close and trash the current request instance.
        :return: Response from the API call
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to close and trash.")
        self.close(note=note, completion_reason=CompletionReason.solved)
        return self.trash()

    def archive(self):
        """
        Archives the current request instance.
        :return: Response from the API call
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to archive.")
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/archive'
        response = self._connection_object.api_call(uri, 'POST')
        return Request.from_data(self._connection_object,response)

    def trash(self):
        """
        Trashes the current request instance.

        :param force: Whether to force the trash operation (if force: the request will be closed and trashed)
        :return: Response from the API call
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to trash.")
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/trash'
        response = self._connection_object.api_call(uri, 'POST')
        return Request.from_data(self._connection_object,response)

    def restore(self):
        """
        Restores the current request instance.
        :return: Response from the API call
        """
        if not self.id:
            raise ValueError("Request instance must have an ID to restore.")
        uri = f'{self._connection_object.base_url}/{self.__resourceUrl__}/{self.id}/restore'
        response = self._connection_object.api_call(uri, 'POST')
        return Request.from_data(self._connection_object,response)
    

    @classmethod
    def create(cls, connection_object: XurrentApiHelper, data: dict):
        """
        Create a new request and return it as an instance of Request.
        :param connection_object: Instance of XurrentApiHelper
        :param data: Dictionary containing request data
        :return: Instance of Request
        """
        uri = f'{connection_object.base_url}/{cls.__resourceUrl__}'
        response = connection_object.api_call(uri, 'POST', data)
        return cls.from_data(connection_object, response)

    # the following methods are for managing configuration items associated with requests
    # Developer Documentation: https://developer.xurrent.com/v1/requests/cis

    @classmethod
    def get_cis_by_request_id(cls, connection_object: XurrentApiHelper, request_id: int) -> List[ConfigurationItem]:
        """
        Retrieve configuration items associated with a request.

        :param connection_object: Xurrent API connection object
        :param request_id: ID of the request
        :return: List of ConfigurationItem objects
        """
        from .configuration_items import ConfigurationItem 
        uri = f'{connection_object.base_url}/requests/{request_id}/cis'
        response = connection_object.api_call(uri, 'GET')
        return [ConfigurationItem.from_data(connection_object, ci) for ci in response]

    @classmethod
    def add_ci_to_request_by_id(cls, connection_object: XurrentApiHelper, request_id: int, ci_id: int) -> bool:
        """
        Link configuration items to a request.

        :param connection_object: Xurrent API connection object
        :param request_id: ID of the request
        :param ci_id: item ID to link
        :return: true if successful, false otherwise
        """
        uri = f'{connection_object.base_url}/requests/{request_id}/cis/{ci_id}'
        try:
            connection_object.api_call(uri, 'POST')
            return True
        except Exception as e:
            return False

    @classmethod
    def remove_ci_from_request_by_id(cls, connection_object: XurrentApiHelper, request_id: int, ci_id: int) -> bool:
        """
        Unlink configuration items from a request.

        :param connection_object: Xurrent API connection object
        :param request_id: ID of the request
        :param ci_id: item ID to unlink
        :return: true if successful, false otherwise
        """
        uri = f'{connection_object.base_url}/requests/{request_id}/cis/{ci_id}'
        try:
            connection_object.api_call(uri, 'DELETE')
            return True
        except Exception as e:
            return False
    
    def get_cis(self) -> List[ConfigurationItem]:
        """
        Retrieve configuration items associated with this request instance.

        :return: List of ConfigurationItem objects
        """
        from .configuration_items import ConfigurationItem
        uri = f'{self._connection_object.base_url}/requests/{self.id}/cis'
        response = self._connection_object.api_call(uri, 'GET')
        return [ConfigurationItem.from_data(self._connection_object, ci) for ci in response]

    def add_ci(self, ci_id: int) -> bool:
        """
        Link configuration items to this request instance.

        :param ci_ids: List of configuration item IDs to link
        :return: true if successful, false otherwise
        """

        uri = f'{self._connection_object.base_url}/requests/{self.id}/cis/{ci_id}'
        try:
            self._connection_object.api_call(uri, 'POST')
            return True
        except Exception as e:
            return False
        

    def remove_ci(self, ci_id: int) -> bool:
        """
        Unlink configuration items from this request instance.

        :param ci_ids: List of configuration item IDs to unlink
        :return: true if successful, false otherwise
        """
        uri = f'{self._connection_object.base_url}/requests/{self.id}/cis/{ci_id}'
        try:
            self._connection_object.api_call(uri, 'DELETE')
            return True
        except Exception as e:
            return False

