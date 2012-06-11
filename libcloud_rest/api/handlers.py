# -*- coding:utf-8 -*-
import copy

try:
    import simplejson as json
except ImportError:
    import json

from werkzeug.wrappers import Response
import libcloud

from libcloud_rest.utils import get_providers_names
from libcloud_rest.utils import get_driver_instance
from libcloud_rest.utils import get_driver_by_provider_name
from libcloud_rest.api.versions import versions
from libcloud_rest.api.parser import parse_request_headers

TEST_QUERY_STRING = 'test=1'


class BaseHandler(object):
    def json_response(self, obj):
        """

        @param obj:
        @return:
        """
        reply = json.dumps(obj, sort_keys=True)
        return Response(reply, mimetype='application/json')


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
    To use this class inherit from it and define _DRIVERS and _Providers.
    """
    _DRIVERS = None
    _Providers = None

    def _get_driver_instance(self):
        provider_name = self.params.get('provider')
        headers = self.request.headers
        api_data = parse_request_headers(headers)
        Driver = get_driver_by_provider_name(
            self._DRIVERS, self._Providers, provider_name)
        if self.request.query_string == TEST_QUERY_STRING:
            from tests.utils import get_driver_mock_http

            Driver_copy = copy.deepcopy(Driver)
            Driver_copy.connectionCls.conn_classes = get_driver_mock_http(
                Driver.__name__)
            driver_instance = get_driver_instance(Driver_copy, **api_data)
        else:
            driver_instance = get_driver_instance(Driver, **api_data)
        return driver_instance

    def providers(self):
        """

        @return:
        """
        response = {
            'providers': get_providers_names(self._Providers),
            }
        return self.json_response(response)


#noinspection PyUnresolvedReferences
class ComputeHandler(BaseServiceHandler):
    from libcloud.compute.providers import Provider as _Providers
    from libcloud.compute.providers import DRIVERS as _DRIVERS

    @staticmethod
    def _render(obj, render_attrs):
        return dict(
            ((a_name, getattr(obj, a_name)) for a_name in render_attrs)
        )

    def list_nodes(self):
        """

        @return:
        """
        driver = self._get_driver_instance()
        nodes = driver.list_nodes()
        render_attrs = ['id', 'name', 'state', 'public_ips']
        resp = [self._render(node, render_attrs) for node in nodes]
        return self.json_response(resp)

    def list_sizes(self):
        """

        @return:
        @rtype:
        """
        driver = self._get_driver_instance()
        sizes = driver.list_sizes()
        render_attrs = ['id', 'name', 'ram', 'bandwidth', 'price']
        resp = [self._render(size, render_attrs) for size in sizes]
        return self.json_response(resp)

    def list_images(self):
        """

        @return:
        @rtype:
        """
        driver = self._get_driver_instance()
        images = driver.list_images()
        render_attrs = ['id', 'name']
        resp = [self._render(image, render_attrs) for image in images]
        return self.json_response(resp)


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
