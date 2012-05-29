# -*- coding:utf-8 -*-
from werkzeug.wrappers import Response
import simplejson as json
import libcloud

from libcloud_rest.utils import get_providers_names
from libcloud_rest.utils import get_driver_instance
from libcloud_rest.utils import get_driver_by_provider_name
from libcloud_rest.api.versions import versions


class BaseHandler(object):
    def json_response(self, obj):
        """

        @param obj:
        @return:
        """
        reply = json.dumps(obj)
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
        username = headers.get('x-auth-user', None)
        api_key = headers.get('x-api-key', None)
        Driver = get_driver_by_provider_name(
            self._DRIVERS, self._Providers, provider_name)
        return get_driver_instance(Driver, username, api_key)

    def providers(self):
        """

        @return:
        """
        response = {
            'providers': get_providers_names(self._Providers),
            }
        return self.json_response(response)


class ComputeHandler(BaseServiceHandler):
    from libcloud.compute.providers import Provider as _Providers
    from libcloud.compute.providers import DRIVERS as _DRIVERS

    @staticmethod
    def _node_render(node):
        render_attrs = ['uuid', 'name', 'state', 'public_ips']
        return dict(
            ((a_name, getattr(node, a_name)) for a_name in render_attrs)
        )

    def list_nodes(self):
        """

        @return:
        """
        driver = self._get_driver_instance()
        nodes = driver.list_nodes()
        resp = [self._node_render(node) for node in nodes]
        return self.json_response(resp)


class StorageHandler(BaseServiceHandler):
    from libcloud.storage.providers import Provider as _Providers
    from libcloud.storage.providers import DRIVERS as _DRIVERS


class LoabBalancerHandler(BaseServiceHandler):
    from libcloud.loadbalancer.providers import Provider as _Providers
    from libcloud.loadbalancer.providers import DRIVERS as _DRIVERS


class DNSHandler(BaseServiceHandler):
    from libcloud.dns.providers import Provider as _Providers
    from libcloud.dns.providers import DRIVERS as _DRIVERS
