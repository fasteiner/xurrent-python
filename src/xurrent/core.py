from __future__ import annotations  # Needed for forward references
from datetime import datetime
from enum import Enum
import time
import requests
import logging
import json
import re
import base64

class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class JsonSerializableDict(dict):
    def __init__(self, **kwargs):
        # Initialize with keyword arguments as dictionary items
        super().__init__(**kwargs)

    def to_dict(self) -> dict:
        """Ensure nested objects are converted to dictionaries."""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):  # Exclude private attributes
                # Recursively call to_dict on nested JsonSerializableDict objects
                if isinstance(value, JsonSerializableDict):
                    result[key] = value.to_dict()
                elif isinstance(value, list):
                    #call to_dict on each item in the list
                    result[key] = [item.to_dict() for item in value]
                elif isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result
    def to_json(self):
        """Convert the dictionary to a JSON string."""
        return json.dumps(self.to_dict())



class XurrentApiHelper:
    api_user: Person # Forward declaration with a string
    api_user_teams: List[Team] # Forward declaration with a string

    def __init__(self, base_url, api_key, api_account,resolve_user=True, logger: Logger=None):
        """
        Initialize the Xurrent API helper.

        :param base_url: Base URL of the Xurrent API
        :param api_key: API key to authenticate with
        :param api_account: Account name to use
        :param resolve_user: Resolve the API user and their teams (default: True)
        :param logger: Logger to use (optional), otherwise a new logger is created
        """
        self.base_url = base_url
        self.api_key = api_key
        self.api_account = api_account
        if logger:
            self.logger = logger
        else:
            self.logger = self.create_logger(False)
        #Create a requests session to maintain persistent connections, with preset headers
        self.__session = requests.Session()
        self.__session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'x-xurrent-account': self.api_account
        })
        if resolve_user:
            # Import Person lazily
            from .people import Person
            self.api_user = Person.get_me(self)
            self.api_user_teams = self.api_user.get_teams()

    def __append_per_page(self, uri, per_page=100):
        """
        Append the 'per_page' parameter to the URI if not already present.
        :param uri: URI to append the parameter to
        :param per_page: Number of records per page
        :return: URI with the 'per_page' parameter appended
        >>> helper = XurrentApiHelper('https://api.example.com', 'api_key', 'account', False)
        >>> helper._XurrentApiHelper__append_per_page('https://api.example.com/tasks')
        'https://api.example.com/tasks?per_page=100'
        >>> helper._XurrentApiHelper__append_per_page('https://api.example.com/tasks?status=open')
        'https://api.example.com/tasks?status=open&per_page=100'
        >>> helper._XurrentApiHelper__append_per_page('https://api.example.com/tasks?status=open&per_page=50')
        'https://api.example.com/tasks?status=open&per_page=50'
        >>> helper._XurrentApiHelper__append_per_page('https://api.example.com/tasks/')
        'https://api.example.com/tasks?per_page=100'
        >>> helper._XurrentApiHelper__append_per_page('https://api.example.com/tasks?per_page=50', 100)
        'https://api.example.com/tasks?per_page=50'
        >>> helper._XurrentApiHelper__append_per_page('https://api.example.com/people/me', 100)
        'https://api.example.com/people/me'

        """
        if '?' in uri and not 'per_page=' in uri:
            return f'{uri}&per_page={per_page}'
        elif not re.search(r'\d$', uri) and not 'per_page=' in uri and not uri.endswith('me'):
            if uri.endswith('/'):
                uri = uri[:-1]
            return f'{uri}?per_page={per_page}'
        return uri

    def create_logger(self, verbose) -> Logger:
        """
        Create a logger for the API helper.
        :param verbose: Enable verbose logging (debug level)
        :return: Logger instance
        """
        logger = logging.getLogger()
        log_stream = logging.StreamHandler()

        if verbose:
            logger.setLevel(logging.DEBUG)
            log_stream.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            log_stream.setLevel(logging.INFO)

        formatter = logging.Formatter('%(levelname)s - %(message)s')
        log_stream.setFormatter(formatter)
        logger.addHandler(log_stream)
        return logger

    def set_log_level(self, level: LogLevel):
        """
        Set the log level for the logger and all handlers.

        :param level: Log level to set
        """
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)


    def api_call(self, uri: str, method='GET', data=None, per_page=100, raw=False):
        """
        Make a call to the Xurrent API with support for rate limiting and pagination.
        :param uri: URI to call
        :param method: HTTP method to use (default: GET)
        :param data: Data to send with the request (optional)
        :param per_page: Number of records per page for GET requests, setting to 0/None disables pagination (default: 100)
        :param raw: Do not process the request result, e.g. in the case of non-JSON data (default: False)
        :return: JSON response from the API or aggregated data for paginated GET
        """
        # Ensure the base URL is included in the URI, if no protocol (https://) specified
        if not uri.startswith(self.base_url) and "://" not in uri[:10]:
            uri = f'{self.base_url}{uri}'

        aggregated_data = []
        next_page_url = uri

        while next_page_url:
            try:
                # Append pagination parameters for GET requests
                if per_page and method == 'GET':
                    # if contains ? or does not end with /, append per_page
                    next_page_url = self.__append_per_page(next_page_url, per_page)

                # Log the request
                self.logger.debug(f'{method} {next_page_url} {data if method != "GET" else ""}')

                # Make the HTTP request
                response = self.__session.request(method, next_page_url, json=data)

                if response.status_code == 204:
                    return None

                # Handle rate limiting (429 status code)
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 1))  # Default to 1 second if not provided
                    self.logger.warning(f'Rate limit reached. Retrying after {retry_after} seconds...')
                    time.sleep(retry_after)
                    continue

                # Check for other non-success status codes
                if not response.ok:
                    self.logger.error(f'Error in request: {response.status_code} - {response.text}')
                    response.raise_for_status()

                #Stop here if we shall not process or interperet the returned data
                if raw:
                    return response.content

                # Process response
                response_data = response.json()

                # For GET requests, handle pagination
                if method == 'GET' and isinstance(response_data, list):
                    aggregated_data.extend(response_data)

                    # Parse the 'Link' header to find the 'next' page URL
                    link_header = response.headers.get('Link')
                    if link_header:
                        links = {rel.strip(): url.strip('<>') for url, rel in
                                (link.split(';') for link in link_header.split(','))}
                        next_page_url = links.get('rel="next"')
                        if next_page_url:
                            next_page_url = next_page_url.replace('<', '').replace('>', '')
                    else:
                        next_page_url = None
                else:
                    return response_data  # Return for non-GET requests

            except requests.exceptions.RequestException as e:
                self.logger.error(f'HTTP request failed: {e}')
                raise

        # Return aggregated results for paginated GET
        return aggregated_data

    def bulk_export(self, type: str, export_format='csv', save_as=None, poll_timeout=5):
        """
        Make a call to the Xurrent API to perform a bulk export
        :param type: Resource type(s) to download, comma-delimited
        :param export_format: either 'csv' or 'xlsx' (Default: csv)
        :param save_as: Save the results to a file instead of returning the raw result
        :param poll_timeout: Seconds to wait between export result polls (Default: 5 seconds)
        :return: CSV or XSLX data from the export, ZIP if multiple types supplied
        """

        #Initiate an export and get the polling token
        export = self.api_call('/export', method = 'POST', data = dict(type = type, export_format = export_format))

        #Begin export results poll waiting loop
        while True:
            self.logger.debug('Export poll wait.')
            time.sleep(poll_timeout)
            result = self.api_call(f"/export/{export['token']}", per_page = None)
            if result['state'] in ('queued','processing'):
                continue
            if result['state'] == 'done':
                break
            self.logger.error(f'Export request failed: {result=}')
            raise

        #Save or Return the exported data
        result = self.api_call(result["url"], per_page = None, raw = True)
        if save_as:
            with open(save_as, 'wb') as file:
                file.write(result)
            return True
        return result

    def custom_fields_to_object(self, custom_fields):
        """
        Convert a list of custom fields to a dictionary.
        :param custom_fields: List of custom fields
        :return: Dictionary containing the custom fields

        >>> helper = XurrentApiHelper('https://api.example.com', 'api_key', 'account', False)
        >>> helper.custom_fields_to_object([{'id': 'priority', 'value': 'high'}, {'id': 'status', 'value': 'open'}])
        {'priority': 'high', 'status': 'open'}
        """
        result = {}
        for field in custom_fields:
            result[field['id']] = field['value']
        return result

    def object_to_custom_fields(self, obj):
        """
        Convert a dictionary to a list of custom fields.
        :param obj: Dictionary to convert
        :return: List of custom fields

        >>> helper = XurrentApiHelper('https://api.example.com', 'api_key', 'account', False)
        >>> helper.object_to_custom_fields({'priority': 'high', 'status': 'open'})
        [{'id': 'priority', 'value': 'high'}, {'id': 'status', 'value': 'open'}]
        """
        result = []
        for key, value in obj.items():
            result.append({'id': key, 'value': value})
        return result

    def create_filter_string(self, filter: dict):
        """
        Create a filter string from a dictionary.
        :param filter: Dictionary containing the filter parameters
        :return: String containing the filter parameters
        >>> helper = XurrentApiHelper('https://api.example.com', 'api_key', 'account', False)
        >>> helper.create_filter_string({'status': 'open', 'priority': 'high'})
        'status=open&priority=high'
        >>> helper.create_filter_string({'status': 'open'})
        'status=open'
        """
        filter_string = ''
        for key, value in filter.items():
            filter_string += f'{key}={value}&'
        return filter_string[:-1]

    def decode_api_id(self, id: str):
        """
        API resource IDs are base64-encoded strings with the padding bytes stripped off.
        Ensure approproate padding and decode.
        :param id: Encoded Xurrent resource ID
        :return: String containing the decoded ID
        >>> helper = XurrentApiHelper('https://api.example.com', 'api_key', 'account', False)
        >>> helper.decode_api_id('SGVsbG8sIHdvcmxkIQ')
        'Hello, world!'
        """
        #Get the length remainder of 4, fill the remainder to be a power of 4, but only if it is not already 4
        padding_count = (4 - (len(id) % 4)) % 4
        padding = "=" * padding_count
        value = id + padding
        return base64.decodebytes(value.encode()).decode()

    def encode_api_id(self, id: str):
        """
        API resource IDs are base64-encoded strings with the padding bytes stripped off.
        Encode and strip padding.
        :param id: Xurrent resource ID to encode
        :return: String containing the encoded ID
        >>> helper = XurrentApiHelper('https://api.example.com', 'api_key', 'account', False)
        >>> helper.encode_api_id('Hello, world!')
        'SGVsbG8sIHdvcmxkIQ'
        """
        return base64.encodebytes(id.encode()).decode().strip().rstrip("=")
