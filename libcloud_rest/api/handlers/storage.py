# -*- coding:utf-8 -*-
from functools import partial
import httplib

from libcloud.storage import providers
from werkzeug.wsgi import wrap_file

from libcloud_rest.api.handlers import ServiceHandler, invoke_method,\
    list_providers, get_driver_instance
from libcloud_rest.utils import json, Response
from libcloud_rest.api import entries


invoke_method = partial(invoke_method, providers)


storage_handler = ServiceHandler('/storage/')


storage_handler.add_handlers([
    ('/providers', partial(list_providers, providers)),
    ('/<string:provider>/containers',
     partial(invoke_method, 'list_containers')),
])


@storage_handler.handler('/<string:provider>/containers', methods=['POST'])
def create_container(request):
    """
    Invoke create_container method and patch response.

    @return: Response object with newly created container name in Location.
    """
    response = invoke_method('create_container', request)
    container_id = json.loads(response.data)['name']
    response.autocorrect_location_header = False
    response.headers.add_header('Location', container_id)
    response.status_code = httplib.CREATED
    return response


@storage_handler.handler('/<string:provider>/containers/<string:container>')
def get_container(request):
    data = {'container_name': request.args['container']}
    return invoke_method('get_container', request, data=json.dumps(data))


@storage_handler.handler('/<string:provider>/containers/<string:container>',
                         methods=['DELETE'])
def delete_container(request):
    data = {'container_name': request.args['container']}
    return invoke_method('delete_container',
                         request, data=json.dumps(data),
                         status_code=httplib.NO_CONTENT)


@storage_handler.handler('/<string:provider>/containers/<string:container>'
                         '/objects/<string:object_name>', methods=['POST'])
def craete_object(request):
    driver = get_driver_instance(providers, request)
    data = {'container_name': request.args['container']}
    container = entries.ContainerEntry._get_object(data, driver)
    extra = {'content_type': request.content_type}
    result = driver.upload_object_via_stream(
        wrap_file(request.environ, request.stream, 8096),
        container, request.args['object_name'], extra)
    return Response(entries.ObjectEntry.to_json(result), status=httplib.OK)


@storage_handler.handler('/<string:provider>/containers/<string:cont>/objects')
def list_objects(request):
    data = {'container_name': request.args['cont']}
    return invoke_method('list_container_objects',
                         request, data=json.dumps(data))


@storage_handler.handler('/<string:provider>/containers/<string:container>/'
                         'objects/<string:object>')
def get_object(request):
    data = {'container_name': request.args['container'],
            'object_name': request.args['object']}
    return invoke_method('download_object_as_stream',
                         request, data=json.dumps(data), file_result=True)


@storage_handler.handler('/<string:provider>/containers/<string:container>/'
                         'objects/<string:object>/metadata')
def get_object_metadata(request):
    data = {'container_name': request.args['container'],
            'object_name': request.args['object']}
    return invoke_method('get_object',
                         request, data=json.dumps(data))


@storage_handler.handler('/<string:provider>/containers/<string:container>/'
                         'objects/<string:object>', methods=['DELETE'])
def delete_object(request):
    data = {'container_name': request.args['container'],
            'object_name': request.args['object']}
    return invoke_method('delete_object', request, data=json.dumps(data))
