# -*- coding:utf-8 -*-
import httplib
import inspect
import traceback

try:
    import simplejson as json
except ImportError:
    import json

from werkzeug.wrappers import Response
import libcloud
from libcloud.compute import base as compute_base
from libcloud.dns import base as dns_base

from libcloud_rest.api.versions import versions
from libcloud_rest.api.parser import parse_request_headers
from libcloud_rest.api import validators as valid
from libcloud_rest.errors import InternalError,\
    LibcloudError, MalformedJSONError, INTERNAL_LIBCLOUD_ERRORS_MAP,\
    ProviderNotSupportedError, MethodParsingException
from libcloud_rest.utils import ExtJSONEndoder
from libcloud_rest.constants import TEST_QUERY_STRING
from libcloud_rest.server import DEBUG
from libcloud_rest.log import logger
from libcloud_rest.api.providers import get_providers_info,\
    get_driver_by_provider_name, get_driver_instance, get_providers_dict,\
    DriverMethod

if DEBUG:
    import mock


class BaseHandler(object):
    obj_attrs = {}

    def json_response(self, obj, status_code=httplib.OK):
        """

        @param status_code:
        @param obj:
        @return:
        """
        encoder = ExtJSONEndoder(self.obj_attrs)
        reply = encoder.encode(obj)
        return Response(reply, mimetype='application/json', status=status_code)


class ApplicationHandler(BaseHandler):
    def index(self):
        """

        @return:
        """
        response = {
            'Project strategic plan': 'http://goo.gl/TIxkg',
            'GitHub page': 'https://github.com/islamgulov/libcloud.rest',
            'libcloud_version': libcloud.__version__,
            'api_version': versions[libcloud.__version__]
        }
        return self.json_response(response)


class BaseServiceHandler(BaseHandler):
    """
    To use this class inherit from it and define _DRIVERS and _Providers
    Also to encode to json response custom object add them to obj_attrs dict.
    """
    _DRIVERS = None
    _Providers = None
    _providers_list_response = None

    def _get_driver_instance(self):
        provider_name = self.params.get('provider')
        headers = self.request.headers
        api_data = parse_request_headers(headers)
        Driver = get_driver_by_provider_name(
            self._DRIVERS, self._Providers, provider_name)
        if self.request.query_string == TEST_QUERY_STRING and DEBUG:
            from tests.utils import get_test_driver_instance
            driver_instance = get_test_driver_instance(Driver, **api_data)
        else:
            driver_instance = get_driver_instance(Driver, **api_data)
        return driver_instance

    def _execute_driver_method(self, method_name, *args, **kwargs):
        driver = self._get_driver_instance()
        method = getattr(driver, method_name, None)
        if not inspect.ismethod(method) and \
                not (DEBUG and isinstance(method, mock.MagicMock)):
            raise InternalError(detail='Unknown method %s' % (method_name))
        try:
            result = method(*args, **kwargs)
        except Exception, e:
            for libcloud_error, error in INTERNAL_LIBCLOUD_ERRORS_MAP.items():
                if isinstance(e, libcloud_error):
                    raise error()
            else:
                logger.debug(traceback.format_exc())
                raise LibcloudError(detail=str(e))
        return result

    def _list_objects_request_execute(self, method_name, *args, **kwargs):
        data = self._execute_driver_method(method_name, *args, **kwargs)
        return self.json_response(data)

    def _load_json(self, data, validator=None):
        try:
            json_data = json.loads(data)
        except (ValueError, TypeError), e:
            raise MalformedJSONError(detail=str(e))
        if validator is not None:
            validator(json_data)
        return json_data

    def providers(self):
        """

        @return:
        """
        if self._providers_list_response is None:
            providers_info = get_providers_info(self._DRIVERS,
                                                self._Providers)
            response = self.json_response(providers_info)
            self.__class__._providers_list_response = response
        return self._providers_list_response


#noinspection PyUnresolvedReferences
class ComputeHandler(BaseServiceHandler):
    from libcloud.compute.providers import Provider as _Providers
    from libcloud.compute.providers import DRIVERS as _DRIVERS

    obj_attrs = {
        compute_base.Node: ['id', 'name', 'state', 'public_ips'],
        compute_base.NodeSize: ['id', 'name', 'ram', 'bandwidth', 'price'],
        compute_base.NodeImage: ['id', 'name'],
        compute_base.NodeLocation: ['id', 'name', 'country']
    }

    list_nodes = lambda self: self._list_objects_request_execute('list_nodes')
    list_sizes = lambda self: self._list_objects_request_execute('list_sizes')
    list_locations = lambda self: self._list_objects_request_execute(
        'list_locations')
    list_images = lambda self: self._list_objects_request_execute(
        'list_images')

    def create_node(self):
        node_validator = valid.DictValidator({
            'name': valid.StringValidator(),
            'size_id': valid.StringValidator(),
            'image_id': valid.StringValidator(),
            'location_id': valid.StringValidator(required=False)
        })
        node_data = self._load_json(self.request.data, node_validator)

        create_node_kwargs = {}
        create_node_kwargs['name'] = node_data['name']
        create_node_kwargs['size'] = compute_base.NodeSize(
            node_data['size_id'], None, None, None, None, None, None)
        create_node_kwargs['image'] = compute_base.NodeImage(
            node_data['image_id'], None, None)
        location_id = node_data.get('location_id', None)
        if location_id is not None:
            create_node_kwargs['location'] = compute_base.NodeLocation(
                node_data['location_id'], None, None, None)
        node = self._execute_driver_method('create_node', **create_node_kwargs)
        return self.json_response(node,
                                  status_code=httplib.CREATED)

    def reboot_node(self):
        """

        @return:This operation does not return a response body.
        """
        node_id = self.params.get('node_id', None)
        node = compute_base.Node(node_id, None, None, None, None, None)
        self._execute_driver_method('reboot_node', node)
        return self.json_response("")

    def destroy_node(self):
        """

        @return:This operation does not return a response body.
        """
        node_id = self.params.get('node_id', None)
        node = compute_base.Node(node_id, None, None, None, None, None)
        self._execute_driver_method('destroy_node', node)
        return self.json_response("", status_code=httplib.NO_CONTENT)

    def provider_info(self):
        provider_name = self.params.get('provider_name', '')
        provider_name = provider_name.upper()
        providers = get_providers_dict(self._DRIVERS, self._Providers)
        if not provider_name in providers:
            raise ProviderNotSupportedError(provider=provider_name)
        driver = providers[provider_name]
        supported_methods = {}
        for method_name, method in inspect.getmembers(driver,
                                                      inspect.ismethod):
            if method_name.startswith('_'):
                continue
            try:
                driver_method = DriverMethod(driver, method_name)
            except MethodParsingException, e:
                logger.info(str(e))
                continue
            supported_methods[method_name] = driver_method.get_description()
        result = {'name': driver.name,
                  'website': driver.website,
                  'supported_methods': supported_methods}
        return self.json_response(result, status_code=httplib.OK)


#noinspection PyUnresolvedReferences
class StorageHandler(BaseServiceHandler):
    from libcloud.storage.providers import Provider as _Providers
    from libcloud.storage.providers import DRIVERS as _DRIVERS


#noinspection PyUnresolvedReferences
class LoabBalancerHandler(BaseServiceHandler):
    from libcloud.loadbalancer.providers import Provider as _Providers
    from libcloud.loadbalancer.providers import DRIVERS as _DRIVERS


#noinspection PyUnresolvedReferences
class DNSHandler(BaseServiceHandler):
    from libcloud.dns.providers import Provider as _Providers
    from libcloud.dns.providers import DRIVERS as _DRIVERS

    obj_attrs = {
        dns_base.Zone: ['id', 'domain', 'type', 'ttl'],
        dns_base.Record: ['id', 'name', 'type', 'data']
    }

    list_zones = lambda self: self._list_objects_request_execute('list_zones')

    def delete_zone(self):
        zone_id = self.params.get('zone_id', None)
        zone = self._execute_driver_method('get_zone', zone_id)
        self._execute_driver_method('delete_zone', zone)
        return self.json_response("", status_code=httplib.NO_CONTENT)

    def list_records(self):
        zone_id = self.params.get('zone_id', None)
        zone = self._execute_driver_method('get_zone', zone_id)
        return self._list_objects_request_execute('list_records', zone=zone)

    def create_zone(self):
        zone_validator = valid.DictValidator({
            'domain': valid.StringValidator(),
            'type': valid.StringValidator(),
            'ttl': valid.IntegerValidator(required=False)
        })
        zone_data = self._load_json(self.request.data, zone_validator)
        create_zone_args = {
            'domain': zone_data['domain'],
            'type': zone_data['type'],
            'ttl': zone_data.get('ttl', None)
        }
        zone = self._execute_driver_method('create_zone', **create_zone_args)
        return self.json_response(zone,
                                  status_code=httplib.CREATED)

    def update_zone(self):
        update_zone_validator = valid.DictValidator({
            'domain': valid.StringValidator(required=False),
            'type': valid.StringValidator(required=False),
            'ttl': valid.IntegerValidator(required=False)
        })
        zone_data = self._load_json(self.request.data, update_zone_validator)
        zone_id = self.params.get('zone_id', None)
        zone = self._execute_driver_method('get_zone', zone_id)
        update_zone_args = {}
        for arg in update_zone_validator.items_validators.keys():
            if zone_data.get(arg, None):
                update_zone_args[arg] = zone_data[arg]
        updated_zone = self._execute_driver_method('update_zone',
                                                   zone, **update_zone_args)
        return self.json_response(updated_zone)

    def get_record(self):
        zone_id = self.params.get('zone_id', None)
        record_id = self.params.get('record_id', None)
        record = self._execute_driver_method('get_record', zone_id=zone_id,
                                             record_id=record_id)
        return self.json_response(record)

    def create_record(self):
        record_validator = valid.DictValidator({
            'name': valid.StringValidator(),
            'type': valid.IntegerValidator(),
            'data': valid.StringValidator(),
        })
        record_data = self._load_json(self.request.data, record_validator)
        zone_id = self.params.get('zone_id', None)
        zone = self._execute_driver_method('get_zone', zone_id)
        create_record_args = {
            'name': record_data['name'],
            'type': record_data['type'],
            'data': record_data['data'],
            'zone': zone,
        }
        record = self._execute_driver_method('create_record',
                                             **create_record_args)
        return self.json_response(record,
                                  status_code=httplib.CREATED)

    def update_record(self):
        update_record_validator = valid.DictValidator({
            'name': valid.StringValidator(required=False),
            'type': valid.IntegerValidator(required=False),
            'data': valid.StringValidator(required=False),
        })
        record_data = self._load_json(self.request.data,
                                      update_record_validator)
        zone_id = self.params.get('zone_id', None)
        record_id = self.params.get('record_id', None)
        record = self._execute_driver_method('get_record', zone_id=zone_id,
                                             record_id=record_id)
        update_record_args = {}
        for arg in update_record_validator.items_validators.keys():
            if record_data.get(arg, None):
                update_record_args[arg] = record_data[arg]
        updated_record = self._execute_driver_method('update_record',
                                                     record,
                                                     **update_record_args)
        return self.json_response(updated_record)

    def delete_record(self):
        zone_id = self.params.get('zone_id', None)
        record_id = self.params.get('record_id', None)
        record = self._execute_driver_method('get_record', zone_id=zone_id,
                                             record_id=record_id)
        self._execute_driver_method('delete_record', record)
        return self.json_response("", status_code=httplib.NO_CONTENT)
