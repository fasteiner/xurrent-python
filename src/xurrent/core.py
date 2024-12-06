from __future__ import annotations  # Needed for forward references
import logging
import requests
import json
import re

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
                else:
                    result[key] = value
        return result
    def to_json(self):
        """Convert the dictionary to a JSON string."""
        return json.dumps(self.to_dict())



class XurrentApiHelper:
    api_user: Person # Forward declaration with a string

    def __init__(self, base_url, api_key, api_account, resolve_user=True):
        self.base_url = base_url
        self.api_key = api_key
        self.api_account = api_account
        self.logger = logging.getLogger(__name__)
        if resolve_user:
            # Import Person lazily
            from .people import Person
            self.api_user = Person.get_me(self)

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

        """
        if '?' in uri and not 'per_page=' in uri:
            return f'{uri}&per_page={per_page}'
        elif not re.search(r'\d$', uri) and not 'per_page=' in uri:
            if uri.endswith('/'):
                uri = uri[:-1]
            return f'{uri}?per_page={per_page}'
        return uri


    def api_call(self, uri: str, method='GET', data=None, per_page=100):
        """
        Make a call to the Xurrent API with support for rate limiting and pagination.
        :param uri: URI to call
        :param method: HTTP method to use
        :param data: Data to send with the request (optional)
        :param per_page: Number of records per page for GET requests (default: 100)
        :return: JSON response from the API or aggregated data for paginated GET
        """
        # Ensure the base URL is included in the URI
        if not uri.startswith(self.base_url):
            uri = f'{self.base_url}{uri}'

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'x-xurrent-account': self.api_account
        }

        aggregated_data = []
        next_page_url = uri

        while next_page_url:
            try:
                # Append pagination parameters for GET requests
                if method == 'GET':
                    # if contains ? or does not end with /, append per_page
                    next_page_url = self.__append_per_page(next_page_url, per_page)

                # Log the request
                self.logger.debug(f'{method} {next_page_url} {data if method != "GET" else ""}')

                # Make the HTTP request
                response = requests.request(method, next_page_url, headers=headers, json=data)

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
                    else:
                        next_page_url = None
                else:
                    return response_data  # Return for non-GET requests

            except requests.exceptions.RequestException as e:
                self.logger.error(f'HTTP request failed: {e}')
                raise

        # Return aggregated results for paginated GET
        return aggregated_data

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