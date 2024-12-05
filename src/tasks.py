from .core import XurrentApiHelper
from .workflows import Workflow


class Task():
    #https://developer.4me.com/v1/tasks/
    resourceUrl = 'tasks'

    @staticmethod
    def get_by_id(connection_object: XurrentApiHelper, id):
        uri = f'{connection_object.base_url}/{Task.resourceUrl}/{id}'
        return connection_object.api_call(uri, 'GET')

    def get_workflow_of_task(connection_object: XurrentApiHelper, id, expand: bool = False):
        task = Task.get_by_id(connection_object, id)
        if expand:
            return Workflow.get_by_id(connection_object, task['workflow'].id)
        return task['workflow']

    @staticmethod
    def update(connection_object: XurrentApiHelper, id, data):
        uri = f'{connection_object.base_url}/{Task.resourceUrl}/{id}'
        return connection_object.api_call(uri, 'PATCH', data)

    @staticmethod
    def delete(connection_object: XurrentApiHelper, id):
        uri = f'{connection_object.base_url}/{Task.resourceUrl}/{id}'
        return connection_object.api_call(uri, 'DELETE')
