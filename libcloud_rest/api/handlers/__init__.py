# -*- coding:utf-8 -*-
import httplib
import inspect

import libcloud
from libcloud.common import types as common_types
from werkzeug.routing import Rule, Submount


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
from libcloud_rest.utils import json, JsonResponse, Response
from tests.utils import get_test_driver_instance

DEBUG = True

if DEBUG:
    import mock


def get_driver_instance_by_request(providers, request):
    provider_name = request.args.get('provider')
    headers = request.headers
    api_data = parse_request_headers(headers)
    Driver = get_driver_by_provider_name(
        providers.DRIVERS, providers.Provider, provider_name)
    if TEST_QUERY_STRING in request.query_string and DEBUG:
        driver_instance = get_test_driver_instance(Driver, api_data)
    else:
        driver_instance = get_driver_instance(Driver, api_data)
    return driver_instance


def invoke_method(providers, method_name, request, status_code=httplib.OK,
                  data=None, file_result=False):
    """
    Invoke method and return response with result represented as json.

    @param file_result: If True wraps result
    """
    if data is None:
        data = request.data
    driver = get_driver_instance_by_request(providers, request)
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
        return Response(result, mimetype='text/plain',
                        direct_passthrough=True)
    return JsonResponse(driver_method.invoke_result_to_json(result),
                        status=status_code)


def invoke_extension_method(providers, request, *args, **kwargs):
    method_name = request.args.get('method_name', None)
    if method_name is None or not method_name.startswith('ex_'):
        raise NoSuchOperationError()
    return invoke_method(providers, method_name, request, *args, **kwargs)


def list_providers(providers, _):
    providers_info = get_providers_info(providers)
    return JsonResponse(json.dumps(providers_info))


def provider_info(providers, request):
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
    providers = get_providers_dict(providers.DRIVERS, providers.Provider)
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
    return JsonResponse(json.dumps(result))


class ServiceHandler(object):
    def __init__(self, url_prefix):
        self.url_prefix = url_prefix
        self._endpoint_handlers = []

    def add_handler(self, path, handler, methods=None):
        if methods is None:
            methods = ['GET']
        rule = Rule(path, endpoint=handler, methods=methods)
        self._endpoint_handlers.append(rule)

    def add_handlers(self, handlers):
        for handler in handlers:
            self.add_handler(*handler)

    def handler(self, path, **options):
        """
        Decorator to register handler as an rule
        """

        def wrapper(f):
            self.add_handler(path, f, **options)
            return f

        return wrapper

    def get_rules(self):
        return Submount(self.url_prefix,
                        self._endpoint_handlers)

app_handler = ServiceHandler('/')


@app_handler.handler('/')
def index(_):
    response = {
        'GitHub page': 'https://github.com/islamgulov/libcloud.rest',
        'libcloud_version': libcloud.__version__,
        'api_version': versions[libcloud.__version__]
    }
    return Response(json.dumps(response))
