from __future__ import annotations  # Needed for forward references
from datetime import datetime
from enum import Enum
import time
import requests
import logging
import json
import re
import base64
from urllib.parse import urlencode
from logging import Logger
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .people import Person
    from .teams import Team

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
    api_user: "Person"
    api_user_teams: List["Team"]

    def __init__(
        self,
        base_url,
        api_key=None,
        api_account=None,
        resolve_user=True,
        logger: Logger=None,
        client_id: Optional[str]=None,
        client_secret: Optional[str]=None
    ):
        """
        Initialize the Xurrent API helper.

        :param base_url: Base URL of the Xurrent API
        :param api_key: API key to authenticate with
        :param api_account: Account name to use
        :param client_id: OAuth client ID to use when fetching an access token
        :param client_secret: OAuth client secret to use when fetching an access token
        :param resolve_user: Resolve the API user and their teams (default: True)
        :param logger: Logger to use (optional), otherwise a new logger is created
        """
        self.base_url = base_url
        self.api_account = api_account
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_expires_at: Optional[float] = None

        if bool(api_key) == bool(client_id and client_secret):
            raise ValueError('Provide either api_key or both client_id and client_secret, but not both.')
        if not self.api_account:
            raise ValueError('api_account must be provided.')

        if logger:
            self.logger = logger
        else:
            self.logger = self.create_logger(False)
        if client_id or client_secret:
            if not (client_id and client_secret):
                raise ValueError('Both client_id and client_secret are required for OAuth authentication.')
            self.api_key = None
            self._obtain_access_token()
        else:
            self.api_key = api_key
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

    def _ensure_access_token(self):
        """Ensure that a valid access token is available."""
        if not self._client_id:
            return

        needs_refresh = self.api_key is None
        if self._token_expires_at is not None:
            needs_refresh = needs_refresh or time.time() >= self._token_expires_at

        if needs_refresh:
            self._obtain_access_token()

    def _obtain_access_token(self):
        """Fetch a new OAuth access token using the client credentials grant."""
        # Dynamically determine the domain from the base_url and preserve regional subdomains
        import urllib.parse
        parsed = urllib.parse.urlparse(self.base_url)
        # Extract the netloc (e.g. api.xurrent.com, api.au.xurrent.com) and replace 'api' with 'oauth'
        netloc_parts = parsed.netloc.split('.')
        if len(netloc_parts) < 2:
            raise ValueError('Invalid base_url for extracting domain')
            
        # Replace the first part (assumed to be 'api') with 'oauth'
        if netloc_parts[0] == 'api':
            netloc_parts[0] = 'oauth'
        else:
            self.logger.warning(f"Expected first domain part to be 'api', got '{netloc_parts[0]}'. Proceeding anyway.")
            netloc_parts[0] = 'oauth'
            
        # Reconstruct the domain preserving all parts including regional subdomains
        oauth_domain = '.'.join(netloc_parts)
        token_url = f'https://{oauth_domain}/token'
        payload = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(token_url, data=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            self.logger.error(f'Failed to obtain OAuth access token: {exc}')
            raise

        data = response.json()
        access_token = data.get('access_token')
        if not access_token:
            self.logger.error('OAuth token response did not contain an access_token.')
            raise ValueError('OAuth token response did not contain an access_token.')

        expires_in = data.get('expires_in', 3600)
        buffer_seconds = 60
        self._token_expires_at = time.time() + max(expires_in - buffer_seconds, 0)
        self.api_key = access_token
        
        # Update session headers if the session exists
        if hasattr(self, '__session'):
            self.__session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
            
        self.logger.debug('Obtained new OAuth access token.')

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

    def set_log_level(self, level):
        """
        Set the log level for the logger and all handlers.

        :param level: Log level to set (can be a string, int, or LogLevel enum)
        """
        # Handle different types of input
        if isinstance(level, LogLevel):
            log_level = level.value
        else:
            log_level = level
            
        self.logger.setLevel(log_level)
        for handler in self.logger.handlers:
            handler.setLevel(log_level)


    def api_call(self, uri: str, method='GET', data=None, per_page=100, raw=False):
        """
        Make a call to the Xurrent API with support for rate limiting and pagination.
        Automatically handles 401 responses by refreshing the OAuth token if client_id and client_secret are provided.
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

        def do_request():
            self._ensure_access_token()
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'x-xurrent-account': self.api_account
            }
            aggregated_data = []
            next_page_url = uri
            while next_page_url:
                try:
                    # Append pagination parameters for GET requests
                    if per_page and method == 'GET':
                        next_page_url = self.__append_per_page(next_page_url, per_page)
                    
                    # Log the request
                    self.logger.debug(f'{method} {next_page_url} {data if method != "GET" else ""}')
                    
                    # Make the HTTP request - use session if available, otherwise direct request
                    if hasattr(self, '__session'):
                        response = self.__session.request(method, next_page_url, json=data)
                    else:
                        response = requests.request(method, next_page_url, headers=headers, json=data)
                    
                    if response.status_code == 204:
                        return None
                    
                    # Handle rate limiting (429 status code)
                    if response.status_code == 429:
                        retry_after = int(response.headers.get('Retry-After', 1))  # Default to 1 second if not provided
                        self.logger.warning(f'Rate limit reached. Retrying after {retry_after} seconds...')
                        time.sleep(retry_after)
                        continue
                    
                    # Handle 401 Unauthorized - signal to outer logic to refresh token and retry
                    if response.status_code == 401 and self._client_id:
                        return '401-refresh'
                    
                    # Check for other non-success status codes
                    if not response.ok:
                        self.logger.error(f'Error in request: {response.status_code} - {response.text}')
                        response.raise_for_status()

                    # Stop here if we shall not process or interpret the returned data
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
                        return response_data
                except requests.exceptions.RequestException as e:
                    self.logger.error(f'HTTP request failed: {e}')
                    raise
            return aggregated_data

        result = do_request()
        if result == '401-refresh':
            self.logger.info('401 Unauthorized received, refreshing OAuth token and retrying request...')
            self._obtain_access_token()
            result = do_request()
            # If we still get the 401-refresh sentinel after a token refresh, something is wrong with auth
            if result == '401-refresh':
                self.logger.error('Still receiving 401 Unauthorized after token refresh, authentication failed')
                raise requests.exceptions.HTTPError('Authentication failed: 401 Unauthorized received even after token refresh')
        return result

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
        export = self.api_call('/export', method='POST', data=dict(type=type, export_format=export_format))
        
        if not isinstance(export, dict) or 'token' not in export:
            self.logger.error(f'Export initialization failed: {export}')
            raise ValueError('Invalid export response: missing token')
        
        token = export['token']

        #Begin export results poll waiting loop
        export_result = None
        while True:
            self.logger.debug('Export poll wait.')
            time.sleep(poll_timeout)
            poll_result = self.api_call(f"/export/{token}", per_page=0)
            
            if not isinstance(poll_result, dict) or 'state' not in poll_result:
                self.logger.error(f'Export polling failed: {poll_result}')
                raise ValueError('Invalid poll response: missing state')
                
            if poll_result['state'] in ('queued', 'processing'):
                continue
            elif poll_result['state'] == 'done':
                export_result = poll_result
                break
            else:
                self.logger.error(f'Export request failed: {poll_result=}')
                raise RuntimeError(f'Export failed with state: {poll_result["state"]}')

        if 'url' not in export_result:
            self.logger.error(f'Export result missing URL: {export_result}')
            raise ValueError('Export result missing download URL')
            
        #Save or Return the exported data
        download_url = export_result["url"]
        result = self.api_call(download_url, per_page=0, raw=True)
        
        # Check if result is bytes, otherwise provide a general error
        if not isinstance(result, bytes):
            self.logger.error('Expected bytes response for export download')
            raise TypeError('Export download returned unexpected type')
            
        if save_as:
            with open(save_as, 'wb') as file:
                file.write(result)
            return True
        return result

    def search(self, query: str, types: list = None) -> list:
        """
        Perform a cross-resource full-text search.
        :param query: Search query string
        :param types: Optional list of resource types to search (e.g. ['request', 'person'])
        :return: List of search results
        """
        params = {'q': query}
        if types:
            params['types'] = ','.join(types)
        uri = f"/search?{urlencode(params)}"
        return self.api_call(uri, 'GET')

    def bulk_import(self, data: str, import_type: str, import_format: str = 'csv') -> dict:
        """
        Perform a bulk import of records.
        :param data: CSV/TSV data as a string
        :param import_type: Resource type to import (e.g. 'people', 'configuration_items')
        :param import_format: Format of the import data ('csv' or 'tsv', default: 'csv')
        :return: Import result from the API
        """
        return self.api_call('/import', method='POST', data={
            'type': import_type,
            'import_format': import_format,
            'data': data
        })

    def list_archive(self, queryfilter: dict = None) -> list:
        """
        List all archived items.
        :param queryfilter: Optional query filter parameters
        :return: List of archived items
        """
        uri = '/archive'
        if queryfilter:
            uri += '?' + self.create_filter_string(queryfilter)
        return self.api_call(uri, 'GET')

    def list_trash(self, queryfilter: dict = None) -> list:
        """
        List all trashed items.
        :param queryfilter: Optional query filter parameters
        :return: List of trashed items
        """
        uri = '/trash'
        if queryfilter:
            uri += '?' + self.create_filter_string(queryfilter)
        return self.api_call(uri, 'GET')

    def list_audit_lines(self, queryfilter: dict = None) -> list:
        """
        List audit log entries.
        :param queryfilter: Optional query filter parameters
        :return: List of audit log entries
        """
        uri = '/audit_lines'
        if queryfilter:
            uri += '?' + self.create_filter_string(queryfilter)
        return self.api_call(uri, 'GET')

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
