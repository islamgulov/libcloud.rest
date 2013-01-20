# -*- coding:utf-8 -*-

from functools import partial
import httplib

from libcloud.loadbalancer import providers

from libcloud_rest.api.handlers import ServiceHandler, invoke_method,\
    invoke_extension_method, list_providers, provider_info
from libcloud_rest.utils import json

invoke_method = partial(invoke_method, providers)

lb_handler = ServiceHandler('/loadbalancer/')


lb_handler.add_handlers([
    ('/providers', partial(list_providers, providers)),
    ('/providers/<string:provider_name>',
        partial(provider_info, providers)),
    ('/<string:provider>/<string:method_name>',
        partial(invoke_extension_method, providers), ['POST']),
    ('/<string:provider>/algorithms',
        partial(invoke_method, 'list_supported_algorithms')),
    ('/<string:provider>/balancers',
        partial(invoke_method, 'list_balancers')),
    ('/<string:provider>/protocols',
        partial(invoke_method, 'list_protocols')),
    ('/<string:provider>/locations', partial(invoke_method, 'list_locations'))
])


@lb_handler.handler('/<string:provider>/balancers', methods=['POST'])
def create_balancer(request):
    """
    Invoke create_balancer method and patch response.

    @return: Response object with newly created balancer ID in Location.
    """
    response = invoke_method('create_balancer', request)
    balancer_id = json.loads(response.data)['id']
    response.autocorrect_location_header = False
    response.headers.add_header('Location', balancer_id)
    response.status_code = httplib.CREATED
    return response


@lb_handler.handler('/<string:provider>/balancers/<string:balancer_id>')
def get_balancer(request):
    data = json.dumps({'balancer_id': request.args['balancer_id']})
    return invoke_method('get_balancer', request, data=data)


@lb_handler.handler('/<string:provider>/balancers/<string:loadbalancer_id>',
                    methods=['PUT'])
def update_balancer(request):
    json_data = json.loads(request.data)
    json_data['loadbalancer_id'] = request.args['loadbalancer_id']
    return invoke_method('update_balancer', request,
                         data=json.dumps(json_data))


@lb_handler.handler('/<string:provider>/balancers/<string:loadbalancer_id>',
                    methods=['DELETE'])
def destroy_balancer(request):
    """
    Get balancer id from params and invoke destroy_balancer driver method.
    @return: Empty response body
    """
    json_data = {'loadbalancer_id': request.args['loadbalancer_id']}
    return invoke_method('destroy_balancer', request,
                         data=json.dumps(json_data),
                         status_code=httplib.ACCEPTED)


@lb_handler.handler('/<string:provider>/balancers/<string:lb_id>/members',
                    methods=['POST'])
def create_member(request):
    json_data = json.loads(request.data)
    json_data['loadbalancer_id'] = request.args['lb_id']
    return invoke_method('balancer_attach_member', request,
                         data=json.dumps(json_data))


@lb_handler.handler('/<string:provider>/balancers/<string:lb_id>/members')
def list_members(request):
    json_data = json.loads(request.data)
    json_data['loadbalancer_id'] = request.args['lb_id']
    return invoke_method('balancer_list_members', request,
                         data=json.dumps(json_data))


@lb_handler.handler(
    '/<string:provider>/balancers/<string:lb_id>/members/<string:member_id>',
    methods=['DELETE'])
def delete_member(request):
    """
    @return:This operation does not return a response body.
    """
    json_data = {'loadbalancer_id': request.args['lb_id'],
                 'member_id': request.args['member_id']}
    return invoke_method('balancer_detach_member', request,
                         data=json.dumps(json_data),
                         status_code=httplib.ACCEPTED)
