# -*- coding:utf-8 -*-

from functools import partial
import httplib

from libcloud.dns import providers

from libcloud_rest.api.handlers import ServiceHandler, invoke_method,\
    invoke_extension_method, list_providers, provider_info
from libcloud_rest.utils import json

invoke_method = partial(invoke_method, providers)

dns_handler = ServiceHandler('/dns/')

dns_handler.add_handlers([
    ('/providers', partial(list_providers, providers)),
    ('/providers/<string:provider_name>',
     partial(provider_info, providers)),
    ('/<string:provider>/<string:method_name>',
     partial(invoke_extension_method, providers), ['POST']),
    ('/<string:provider>/zones', partial(invoke_method, 'list_zones')),
    ('/<string:provider>/images', partial(invoke_method, 'list_images')),
    ('/<string:provider>/sizes', partial(invoke_method, 'list_sizes')),
    ('/<string:provider>/locations', partial(invoke_method, 'list_locations'))
])


@dns_handler.handler('/<string:provider>/zones/<string:zone_id>/records')
def list_recods(request):
    json_data = {'zone_id': request.args['zone_id']}
    return invoke_method('list_records', request, data=json.dumps(json_data))


@dns_handler.handler('/<string:provider>/zones', methods=['POST'])
def create_zone(request):
    """
    Invoke create_zone method and patch response.

    @return: Response object with newly created zone ID in Location.
    """
    response = invoke_method('create_zone', request)
    zone_id = json.loads(response.data)['id']
    response.autocorrect_location_header = False
    response.headers.add_header('Location', zone_id)
    response.status_code = httplib.CREATED
    return response


@dns_handler.handler('/<string:provider>/zones/<string:zone_id>',
                     methods=['PUT'])
def update_zone(request):
    json_data = json.loads(request.data)
    json_data['zone_id'] = request.args['zone_id']
    return invoke_method('update_zone', request, data=json.dumps(json_data))


@dns_handler.handler('/<string:provider>/zones/<string:zone_id>',
                     methods=['DELETE'])
def delete_zone(request):
    json_data = {'zone_id': request.args['zone_id']}
    return invoke_method('delete_zone', request, data=json.dumps(json_data),
                         status_code=httplib.ACCEPTED)


@dns_handler.handler(
    '/<string:provider>/zones/<zone_id>/records/<string:record_id>')
def get_record(request):
    json_data = {'zone_id': request.args['zone_id'],
                 'record_id': request.args['record_id']}
    return invoke_method('get_record', request, data=json.dumps(json_data))


@dns_handler.handler('/<string:provider>/zones/<zone_id>/records',
                     methods=['POST'])
def create_record(request):
    json_data = json.loads(request.data)
    json_data['zone_id'] = request.args['zone_id']
    response = invoke_method('create_record',
                             request, data=json.dumps(json_data),
                             status_code=httplib.ACCEPTED)
    record_id = json.loads(response.data)['id']
    response.autocorrect_location_header = False
    response.headers.add_header('Location', record_id)
    response.status_code = httplib.CREATED
    return response


@dns_handler.handler(
    '/<string:provider>/zones/<zone_id>/records/<string:record_id>',
    methods=['PUT'])
def update_record(request):
    json_data = json.loads(request.data)
    json_data['zone_id'] = request.args['zone_id']
    json_data['record_id'] = request.args['record_id']
    return invoke_method('update_record', request, data=json.dumps(json_data))


@dns_handler.handler(
    '/<string:provider>/zones/<zone_id>/records/<string:record_id>',
    methods=['DELETE'])
def delete_record(request):
    json_data = {'zone_id': request.args['zone_id'],
                 'record_id': request.args['record_id']}
    return invoke_method('delete_record', request, data=json.dumps(json_data),
                         status_code=httplib.ACCEPTED)
