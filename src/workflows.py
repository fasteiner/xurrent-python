from .core import XurrentApiHelper


class Workflow():
    #https://developer.4me.com/v1/workflows/
    resourceUrl = 'workflows'

    @staticmethod
    def get_by_id(connection_object: XurrentApiHelper, id):
        uri = f'{connection_object.base_url}/{Workflow.resourceUrl}/{id}'
        return connection_object.api_call(uri, 'GET')

    @staticmethod
    def get_workflow_task_by_template_id(connection_object: XurrentApiHelper, workflowID: int, templateID: int):
        uri = f'{connection_object.base_url}/{Workflow.resourceUrl}/{workflowID}/tasks?template={templateID}'
        tasks = connection_object.api_call(uri, 'GET')
        if len(tasks) == 0:
            return None
        if len(tasks) > 1:
            raise Exception(f"Multiple tasks found for templateID: {templateID}")
        return tasks[0]

    @staticmethod
    def get_workflow_tasks_by_workflow_id(connection_object: XurrentApiHelper, id: int):
        uri = f'{connection_object.base_url}/{Workflow.resourceUrl}/{id}/tasks'
        return connection_object.api_call(uri, 'GET')

    @staticmethod
    def update(connection_object: XurrentApiHelper, id, data):
        uri = f'{connection_object.base_url}/{Workflow.resourceUrl}/{id}'
        return connection_object.api_call(uri, 'PATCH', data)

    @staticmethod
    def delete(connection_object: XurrentApiHelper, id):
        uri = f'{connection_object.base_url}/{Workflow.resourceUrl}/{id}'
        return connection_object.api_call(uri, 'DELETE')
