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
from libcloud.loadbalancer import base as lb_base
from libcloud.common import types as common_types

from libcloud_rest.api.versions import versions
from libcloud_rest.api.parser import parse_request_headers,\
    ARGS_TO_XHEADERS_DICT
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

    def json_response(self, obj, headers=(), status_code=httplib.OK):
        """

        @param status_code:
        @param obj:
        @return:
        """
        encoder = ExtJSONEndoder(self.obj_attrs)
        reply = encoder.encode(obj)
        return Response(reply, mimetype='application/json',
                        headers=headers, status=status_code)


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
        if TEST_QUERY_STRING in self.request.query_string and DEBUG:
            from tests.utils import get_test_driver_instance

            driver_instance = get_test_driver_instance(Driver, **api_data)
        else:
            driver_instance = get_driver_instance(Driver, **api_data)
        return driver_instance

    def _execute_driver_method(self, method_name, *args, **kwargs):
        """
        @deprecated
        """
        driver = self._get_driver_instance()
        method = getattr(driver, method_name, None)
        if not inspect.ismethod(method) and\
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
        """
        @deprecated
        """
        data = self._execute_driver_method(method_name, *args, **kwargs)
        return self.json_response(data)

    def _load_json(self, data, validator=None):
        """
        @deprecated
        """
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

    def provider_info(self):
        """
        Introspect provider class and return response what contain:
        name - provider.name attribute
        website - provider.website attribute
        x-headers - list of provider API credentials which user should provide
            in request headers  (parsed from from __init__ method docstrings)
        supported_methods - list of all methods information which supported by
            provider, Method information parsed from method docstings
        """
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
                logger.info(str(e) + ' ' + driver.name + '.' + method_name)
                continue
            supported_methods[method_name] = driver_method.get_description()
        init_description = DriverMethod(driver, '__init__').get_description()
        init_arguments = init_description['arguments']
        for arg in init_arguments[:]:
            arg['name'] = ARGS_TO_XHEADERS_DICT[arg['name']]
        result = {'name': driver.name,
                  'website': driver.website,
                  'x-headers': init_arguments,
                  'supported_methods': supported_methods}
        return self.json_response(result, status_code=httplib.OK)

    def invoke_method(self, status_code=httplib.OK, data=None):
        """
        Invoke method and return response with result represented as json.
        """
        if data is None:
            data = self.request.data
        driver = self._get_driver_instance()
        method_name = self.params.get('method_name')
        driver_method = DriverMethod(driver, method_name)
        try:
            result = driver_method.invoke(data)
        except Exception, e:
            if e.__class__ in INTERNAL_LIBCLOUD_ERRORS_MAP:
                raise INTERNAL_LIBCLOUD_ERRORS_MAP[e.__class__]()
            if isinstance(e, common_types.LibcloudError):
                raise LibcloudError(detail=str(e))
            raise
        return Response(driver_method.invoke_result_to_json(result),
                        mimetype='application/json',
                        status=status_code)


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

    def create_node(self):
        """
        Invoke create_node method and patch response.

        @return: Response object with newly created node ID in Location.
        """
        response = self.invoke_method()
        node_id = json.loads(response.data)['id']
        response.autocorrect_location_header = False
        response.headers.add_header('Location', node_id)
        response.status_code = httplib.CREATED
        return response

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


#noinspection PyUnresolvedReferences
class StorageHandler(BaseServiceHandler):
    from libcloud.storage.providers import Provider as _Providers
    from libcloud.storage.providers import DRIVERS as _DRIVERS


#noinspection PyUnresolvedReferences
class LoadBalancerHandler(BaseServiceHandler):
    from libcloud.loadbalancer.providers import Provider as _Providers
    from libcloud.loadbalancer.providers import DRIVERS as _DRIVERS

    def create_balancer(self):
        """
        Invoke create_balancer method and patch response.

        @return: Response object with newly created balancer ID in Location.
        """
        response = self.invoke_method()
        balancer_id = json.loads(response.data)['id']
        response.autocorrect_location_header = False
        response.headers.add_header('Location', balancer_id)
        response.status_code = httplib.CREATED
        return response

    def destroy_balancer(self):
        """
        Get balancer id from params and invoke destroy_balancer driver method.
        @return: Empty response body
        """
        json_data = {'loadbalancer_id': self.params['loadbalancer_id']}
        return self.invoke_method(data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)

    def patch_request_and_invoke(self):
        """
        Get balancer id from params and  add it to request data.
        @return: Balancer information in response body
        """
        json_data = json.loads(self.request.data)
        json_data['loadbalancer_id'] = self.params['loadbalancer_id']
        self.request.data = json.dumps(json_data)
        return self.invoke_method()

    def get_balancer(self):
        data = json.dumps({'balancer_id': self.params['balancer_id']})
        return self.invoke_method(data=data)

    def detach_member(self):
        """
        @return:This operation does not return a response body.
        """
        json_data = {'loadbalancer_id': self.params['loadbalancer_id'],
                     'member_id': self.params['member_id']}
        return self.invoke_method(data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)


#noinspection PyUnresolvedReferences
class DNSHandler(BaseServiceHandler):
    from libcloud.dns.providers import Provider as _Providers
    from libcloud.dns.providers import DRIVERS as _DRIVERS

    obj_attrs = {
        dns_base.Zone: ['id', 'domain', 'type', 'ttl'],
        dns_base.Record: ['id', 'name', 'type', 'data']
    }

    def extract_zone_id_and_invoke(self):
        """
        Get zone id from params and add it to request data.
        """
        json_data = json.loads(self.request.data)
        json_data['zone_id'] = self.params['zone_id']
        return self.invoke_method(data=json.dumps(json_data))

    def extract_zone_record_and_invoke(self):
        """
        Get zone id from params and add it to request data.
        """
        json_data = json.loads(self.request.data)
        json_data['zone_id'] = self.params['zone_id']
        json_data['record_id'] = self.params['record_id']
        self.request.data = json.dumps(json_data)
        return self.invoke_method()

    def create_zone(self):
        """
        Invoke create_zone method and patch response.

        @return: Response object with newly created balancer ID in Location.
        """
        response = self.invoke_method()
        zone_id = json.loads(response.data)['id']
        response.autocorrect_location_header = False
        response.headers.add_header('Location', zone_id)
        response.status_code = httplib.CREATED
        return response

    def delete_zone(self):
        """
        @return:This operation does not return a response body.
        """
        json_data = {'zone_id': self.params['zone_id']}
        return self.invoke_method(data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)

    def create_record(self):
        json_data = json.loads(self.request.data)
        json_data['zone_id'] = self.params['zone_id']
        response = self.invoke_method(data=json.dumps(json_data),
                                      status_code=httplib.ACCEPTED)
        record_id = json.loads(response.data)['id']
        response.autocorrect_location_header = False
        response.headers.add_header('Location', record_id)
        response.status_code = httplib.CREATED
        return response

    def delete_record(self):
        json_data = {'zone_id': self.params['zone_id'],
                     'record_id': self.params['record_id']}
        return self.invoke_method(data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)
