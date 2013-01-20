# -*- coding:utf-8 -*-
from functools import partial
import httplib

from libcloud.compute import providers

from libcloud_rest.api.handlers import ServiceHandler, invoke_method,\
    invoke_extension_method, list_providers, provider_info
from libcloud_rest.utils import json

invoke_method = partial(invoke_method, providers)

compute_handler = ServiceHandler('/compute/')

compute_handler.add_handlers([
    ('/providers', partial(list_providers, providers)),
    ('/providers/<string:provider_name>',
     partial(provider_info, providers)),
    ('/<string:provider>/<string:method_name>',
        partial(invoke_extension_method, providers), ['POST']),
    ('/<string:provider>/nodes', partial(invoke_method, 'list_nodes')),
    ('/<string:provider>/images', partial(invoke_method, 'list_images')),
    ('/<string:provider>/sizes', partial(invoke_method, 'list_sizes')),
    ('/<string:provider>/locations', partial(invoke_method, 'list_locations'))
])


@compute_handler.handler('/<string:provider>/nodes', methods=['POST'])
def create_node(request):
    """
    Invoke create_node method and patch response.

    @return: Response object with newly created node ID in Location.
    """
    response = invoke_method('create_node', request)
    node_id = json.loads(response.data)['id']
    response.autocorrect_location_header = False
    response.headers.add_header('Location', node_id)
    response.status_code = httplib.CREATED
    return response


@compute_handler.handler('/<string:provider>/nodes/<string:node_id>/reboot',
                         methods=['PUT'])
def reboot_node(request):
    json_data = {'node_id': request.args['node_id']}
    return invoke_method('reboot_node', request, data=json.dumps(json_data),
                         status_code=httplib.ACCEPTED)


@compute_handler.handler('/<string:provider>/nodes/<string:node_id>',
                         methods=['DELETE'])
def destroy_node(request):
    json_data = {'node_id': request.args['node_id']}
    return invoke_method('destroy_node', request, data=json.dumps(json_data),
                         status_code=httplib.ACCEPTED)
