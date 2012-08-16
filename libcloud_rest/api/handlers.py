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
        return Response(json.dumps(response))


class BaseServiceHandler(object):
    """
    To use this class inherit from it and define _DRIVERS and _Providers
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

    def providers(self):
        """

        @return:
        """
        if self._providers_list_response is None:
            providers_info = get_providers_info(self._DRIVERS,
                                                self._Providers)
            response = Response(json.dumps(providers_info),
                                mimetype='application/json', status=httplib.OK)
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
                  'X-headers': init_arguments,
                  'supported_methods': supported_methods}
        return Response(json.dumps(result), mimetype='application/json',
                        status=httplib.OK)

    def invoke_method(self, status_code=httplib.OK, data=None,
                      file_result=False):
        """
        Invoke method and return response with result represented as json.

        @param file_result: If True wraps result
        """
        if data is None:
            data = self.request.data
        driver = self._get_driver_instance()
        method_name = self.params.get('method_name', None)
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

    def invoke_extension_method(self, *args, **kwargs):
        method_name = self.params.get('method_name', None)
        if method_name is None or not method_name.startswith('ex_'):
            raise NoSuchOperationError()
        return self.invoke_method()


#noinspection PyUnresolvedReferences
class ComputeHandler(BaseServiceHandler):
    from libcloud.compute.providers import Provider as _Providers
    from libcloud.compute.providers import DRIVERS as _DRIVERS

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
        json_data = {'node_id': self.params['node_id']}
        return self.invoke_method(data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)

    def destroy_node(self):
        json_data = {'node_id': self.params['node_id']}
        return self.invoke_method(data=json.dumps(json_data),
                                  status_code=httplib.ACCEPTED)


#noinspection PyUnresolvedReferences
class StorageHandler(BaseServiceHandler):
    from libcloud.storage.providers import Provider as _Providers
    from libcloud.storage.providers import DRIVERS as _DRIVERS

    def get_container(self):
        data = {'container_name': self.params['container_name']}
        return self.invoke_method(data=json.dumps(data))

    def create_container(self):
        """
        Invoke create_container method and patch response.

        @return: Response object with newly created container name in Location.
        """
        response = self.invoke_method()
        balancer_id = json.loads(response.data)['name']
        response.autocorrect_location_header = False
        response.headers.add_header('Location', balancer_id)
        response.status_code = httplib.CREATED
        return response

    def delete_container(self):
        data = {'container_name': self.params['container_name']}
        return self.invoke_method(data=json.dumps(data),
                                  status_code=httplib.NO_CONTENT)

    def extract_params_and_invoke(self):
        """
        Get container name and object name from params
            and add it to request data.
        """
        if self.request.data:
            data = json.loads(self.request.data)
        else:
            data = {}
        data['container_name'] = self.params['container_name']
        if 'object_name' in self.params:
            data['object_name'] = self.params['object_name']
        return self.invoke_method(data=json.dumps(data))

    def download_object(self):
        data = {}
        data['container_name'] = self.params['container_name']
        data['object_name'] = self.params['object_name']
        return self.invoke_method(data=json.dumps(data), file_result=True)

    def upload_object(self):
        driver = self._get_driver_instance()
        data = {'container_name': self.params['container_name']}
        container = entries.ContainerEntry._get_object(data, driver)
        extra = {'content_type': self.request.content_type}
        result = driver.upload_object_via_stream(
            wrap_file(self.request.environ, self.request.stream, 8096),
            container, self.params['object_name'], extra)
        return Response(entries.ObjectEntry.to_json(result), status=httplib.OK)


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
