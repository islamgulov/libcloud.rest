# -*- coding:utf-8 -*-
import httplib
import inspect

from werkzeug.wrappers import Response
import libcloud
from libcloud.common import types as common_types
from werkzeug.wsgi import wrap_file

from libcloud_rest.api.versions import versions
from libcloud_rest.api.parser import parse_request_headers,\
    ARGS_TO_XHEADERS_DICT
from libcloud_rest.errors import LibcloudError, INTERNAL_LIBCLOUD_ERRORS_MAP,\
    ProviderNotSupportedError, MethodParsingException, NoSuchOperationError
from libcloud_rest.constants import TEST_QUERY_STRING
from libcloud_rest.server import DEBUG
from libcloud_rest.log import logger
from libcloud_rest.api.providers import get_providers_info,\
    get_driver_by_provider_name, get_driver_instance, get_providers_dict,\
    DriverMethod
from libcloud_rest.utils import json
from libcloud_rest.api import entries

if DEBUG:
    import mock


class ApplicationHandler(object):
    def index(self, request):
        """

        @return:
        """
        response = {
            'Project strategic plan': 'http://goo.gl/TIxkg',
            'GitHub page': 'https://github.com/islamgulov/libcloud.rest',
            'libcloud_version': libcloud.__version__,
            'api_version': versions[libcloud.__version__]
        }
        return Response(json.dumps(response))


class BaseServiceHandler(object):
    """
    To use this class inherit from it and define _DRIVERS and _Providers
    """
    _DRIVERS = None
    _Providers = None
    _providers_list_response = None

    @classmethod
    def _get_driver_instance(cls, request):
        provider_name = request.args.get('provider')
        headers = request.headers
        api_data = parse_request_headers(headers)
        Driver = get_driver_by_provider_name(
            cls._DRIVERS, cls._Providers, provider_name)
        if TEST_QUERY_STRING in request.query_string and DEBUG:
            from tests.utils import get_test_driver_instance

            driver_instance = get_test_driver_instance(Driver, **api_data)
        else:
            driver_instance = get_driver_instance(Driver, **api_data)
        return driver_instance

    @classmethod
    def providers(cls, request):
        """

        @return:
        """
        if cls._providers_list_response is None:
            providers_info = get_providers_info(cls._DRIVERS,
                                                cls._Providers)
            response = Response(json.dumps(providers_info),
                                mimetype='application/json', status=httplib.OK)
            cls._providers_list_response = response
        return cls._providers_list_response

    @classmethod
    def provider_info(cls, request):
        """
        Introspect provider class and return response what contain:
        name - provider.name attribute
        website - provider.website attribute
        x-headers - list of provider API credentials which user should provide
            in request headers  (parsed from from __init__ method docstrings)
        supported_methods - list of all methods information which supported by
            provider, Method information parsed from method docstings
        """
        provider_name = request.args.get('provider_name', '')
        provider_name = provider_name.upper()
        providers = get_providers_dict(cls._DRIVERS, cls._Providers)
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
                  'X-headers': init_arguments,
                  'supported_methods': supported_methods}
        return Response(json.dumps(result), mimetype='application/json',
                        status=httplib.OK)

    @classmethod
    def invoke_method(cls, request, status_code=httplib.OK, data=None,
                      file_result=False):
        """
        Invoke method and return response with result represented as json.

        @param file_result: If True wraps result
        """
        if data is None:
            data = request.data
        driver = cls._get_driver_instance(request)
        method_name = request.args.get('method_name', None)
        driver_method = DriverMethod(driver, method_name)
        try:
            result = driver_method.invoke(data)
        except Exception, e:
            if e.__class__ in INTERNAL_LIBCLOUD_ERRORS_MAP:
                raise INTERNAL_LIBCLOUD_ERRORS_MAP[e.__class__]()
            if isinstance(e, common_types.LibcloudError):
                raise LibcloudError(detail=str(e))
            raise
        if file_result:
            return Response(result, status=httplib.OK,
                            direct_passthrough=True)
        return Response(driver_method.invoke_result_to_json(result),
                        mimetype='application/json',
                        status=status_code)

    def invoke_extension_method(self, request, *args, **kwargs):
        method_name = request.args.get('method_name', None)
        if method_name is None or not method_name.startswith('ex_'):
            raise NoSuchOperationError()
        return self.invoke_method(request)


class ComputeHandler(BaseServiceHandler):
    from libcloud.compute.providers import Provider as _Providers
    from libcloud.compute.providers import DRIVERS as _DRIVERS

    @classmethod
    def create_node(cls, request):
        """
        Invoke create_node method and patch response.

        @return: Response object with newly created node ID in Location.
        """
        response = cls.invoke_method(request)
        node_id = json.loads(response.data)['id']
        response.autocorrect_location_header = False
        response.headers.add_header('Location', node_id)
        response.status_code = httplib.CREATED
        return response

    @classmethod
    def reboot_node(cls, request):
        json_data = {'node_id': request.args['node_id']}
        return cls.invoke_method(request, data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)

    @classmethod
    def destroy_node(cls, request):
        json_data = {'node_id': request.args['node_id']}
        return cls.invoke_method(request, data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)


class StorageHandler(BaseServiceHandler):
    from libcloud.storage.providers import Provider as _Providers
    from libcloud.storage.providers import DRIVERS as _DRIVERS

    @classmethod
    def get_container(cls, request):
        data = {'container_name': request.args['container_name']}
        return cls.invoke_method(request, data=json.dumps(data))

    @classmethod
    def create_container(cls, request):
        """
        Invoke create_container method and patch response.

        @return: Response object with newly created container name in Location.
        """
        response = cls.invoke_method(request)
        balancer_id = json.loads(response.data)['name']
        response.autocorrect_location_header = False
        response.headers.add_header('Location', balancer_id)
        response.status_code = httplib.CREATED
        return response

    @classmethod
    def delete_container(cls, request):
        data = {'container_name': request.args['container_name']}
        return cls.invoke_method(request, data=json.dumps(data),
                                  status_code=httplib.NO_CONTENT)

    @classmethod
    def extract_params_and_invoke(cls, request):
        """
        Get container name and object name from params
            and add it to request data.
        """
        if request.data:
            data = json.loads(request.data)
        else:
            data = {}
        data['container_name'] = request.args['container_name']
        if 'object_name' in request.args:
            data['object_name'] = request.args['object_name']
        return cls.invoke_method(request, data=json.dumps(data))

    @classmethod
    def download_object(cls, request):
        data = {
            'container_name': request.args['container_name'],
            'object_name': request.args['object_name']
        }
        return cls.invoke_method(request, data=json.dumps(data), file_result=True)

    @classmethod
    def upload_object(cls, request):
        driver = cls._get_driver_instance(request)
        data = {'container_name': request.args['container_name']}
        container = entries.ContainerEntry._get_object(data, driver)
        extra = {'content_type': request.content_type}
        result = driver.upload_object_via_stream(
            wrap_file(request.environ, request.stream, 8096),
            container, request.args['object_name'], extra)
        return Response(entries.ObjectEntry.to_json(result), status=httplib.OK)

class LoadBalancerHandler(BaseServiceHandler):
    from libcloud.loadbalancer.providers import Provider as _Providers
    from libcloud.loadbalancer.providers import DRIVERS as _DRIVERS

    @classmethod
    def create_balancer(cls, request):
        """
        Invoke create_balancer method and patch response.

        @return: Response object with newly created balancer ID in Location.
        """
        response = cls.invoke_method(request)
        balancer_id = json.loads(response.data)['id']
        response.autocorrect_location_header = False
        response.headers.add_header('Location', balancer_id)
        response.status_code = httplib.CREATED
        return response

    @classmethod
    def destroy_balancer(cls, request):
        """
        Get balancer id from params and invoke destroy_balancer driver method.
        @return: Empty response body
        """
        json_data = {'loadbalancer_id': request.args['loadbalancer_id']}
        return cls.invoke_method(request, data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)

    @classmethod
    def patch_request_and_invoke(cls, request):
        """
        Get balancer id from params and  add it to request data.
        @return: Balancer information in response body
        """
        json_data = json.loads(request.data)
        json_data['loadbalancer_id'] = request.args['loadbalancer_id']
        return cls.invoke_method(request, data=json.dumps(json_data))

    @classmethod
    def get_balancer(cls, request):
        data = json.dumps({'balancer_id': request.args['balancer_id']})
        return cls.invoke_method(request, data=data)

    @classmethod
    def detach_member(cls, request):
        """
        @return:This operation does not return a response body.
        """
        json_data = {'loadbalancer_id': request.args['loadbalancer_id'],
                     'member_id': request.args['member_id']}
        return cls.invoke_method(request, data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)


class DNSHandler(BaseServiceHandler):
    from libcloud.dns.providers import Provider as _Providers
    from libcloud.dns.providers import DRIVERS as _DRIVERS

    @classmethod
    def extract_zone_id_and_invoke(cls, request):
        """
        Get zone id from params and add it to request data.
        """
        json_data = json.loads(request.data)
        json_data['zone_id'] = request.args['zone_id']
        return cls.invoke_method(request, data=json.dumps(json_data))

    @classmethod
    def extract_zone_record_and_invoke(cls, request):
        """
        Get zone id from params and add it to request data.
        """
        json_data = json.loads(request.data)
        json_data['zone_id'] = request.args['zone_id']
        json_data['record_id'] = request.args['record_id']
        return cls.invoke_method(request, data=json.dumps(json_data))

    @classmethod
    def create_zone(cls, request):
        """
        Invoke create_zone method and patch response.

        @return: Response object with newly created balancer ID in Location.
        """
        response = cls.invoke_method(request)
        zone_id = json.loads(response.data)['id']
        response.autocorrect_location_header = False
        response.headers.add_header('Location', zone_id)
        response.status_code = httplib.CREATED
        return response

    @classmethod
    def delete_zone(cls, request):
        """
        @return:This operation does not return a response body.
        """
        json_data = {'zone_id': request.args['zone_id']}
        return cls.invoke_method(request, data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)

    @classmethod
    def create_record(cls, request):
        json_data = json.loads(request.data)
        json_data['zone_id'] = request.args['zone_id']
        response = cls.invoke_method(request, data=json.dumps(json_data),
                                      status_code=httplib.ACCEPTED)
        record_id = json.loads(response.data)['id']
        response.autocorrect_location_header = False
        response.headers.add_header('Location', record_id)
        response.status_code = httplib.CREATED
        return response

    @classmethod
    def delete_record(cls, request):
        json_data = {'zone_id': request.args['zone_id'],
                     'record_id': request.args['record_id']}
        return cls.invoke_method(request, data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)
