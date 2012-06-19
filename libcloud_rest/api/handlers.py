# -*- coding:utf-8 -*-
import copy
import httplib

try:
    import simplejson as json
except ImportError:
    import json

from werkzeug.wrappers import Response
import libcloud
from libcloud.compute import base as compute_base

from libcloud_rest.utils import get_providers_dict
from libcloud_rest.utils import get_driver_instance
from libcloud_rest.utils import get_driver_by_provider_name
from libcloud_rest.api.versions import versions
from libcloud_rest.api.parser import parse_request_headers
from libcloud_rest.api import validators as valid
from libcloud_rest.exception import LibcloudRestError,\
    LibcloudError, MalformedJSONError
from libcloud_rest.utils import ExtJSONEndoder
from libcloud_rest.constants import TEST_QUERY_STRING


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
        if self._providers_list_response is None:
            providers_dict = get_providers_dict(self._DRIVERS,
                                      self._Providers)
            response = self.json_response(providers_dict)
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

    def list_nodes(self):
        """

        @return:
        """
        driver = self._get_driver_instance()
        nodes = driver.list_nodes()
        return self.json_response(nodes)

    def list_sizes(self):
        """

        @return:
        @rtype:
        """
        driver = self._get_driver_instance()
        sizes = driver.list_sizes()
        return self.json_response(sizes)

    def list_images(self):
        """

        @return:
        @rtype:
        """
        driver = self._get_driver_instance()
        images = driver.list_images()
        return self.json_response(images)

    def list_locations(self):
        """

        @return:
        @rtype:
        """
        driver = self._get_driver_instance()
        locations = driver.list_locations()
        return self.json_response(locations)

    def create_node(self):
        node_validator = valid.DictValidator({
            'name': valid.StringValidator(),
            'size_id': valid.StringValidator(),
            'image_id': valid.StringValidator(),
            'location_id': valid.StringValidator(required=False)
        })
        driver = self._get_driver_instance()
        try:
            node_data = json.loads(self.request.data)
        except ValueError, e:
            raise MalformedJSONError(msg=e.message)
        node_validator(node_data)
        create_node_kwargs = {}
        create_node_kwargs['name'] = node_data['name']
        create_node_kwargs['size'] = compute_base.NodeSize(
            node_data['size_id'], None, None, None, None, None, driver)
        create_node_kwargs['image'] = compute_base.NodeImage(
            node_data['image_id'], None, driver)
        location_id = node_data.get('location_id', None)
        if location_id is not None:
            create_node_kwargs['location'] = compute_base.NodeLocation(
                node_data['location_id'], None, None, driver)
        try:
            node = driver.create_node(**create_node_kwargs)
        except Exception, e:
            raise LibcloudError(error=str(e))
        return self.json_response(node,
                                  status_code=httplib.CREATED)

    def reboot_node(self):
        """

        @return:This operation does not return a response body.
        """
        driver = self._get_driver_instance()
        node_id = self.params.get('node_id', None)
        node = compute_base.Node(node_id, None, None, None, None, driver)
        try:
            driver.reboot_node(node)
        except Exception, e:  # FIXME
            raise LibcloudError(error=str(e))
        return self.json_response("")

    def destroy_node(self):
        """

        @return:This operation does not return a response body.
        """
        driver = self._get_driver_instance()
        node_id = self.params.get('node_id', None)
        node = compute_base.Node(node_id, None, None, None, None, driver)
        try:
            driver.destroy_node(node)
        except Exception, e:
            raise LibcloudError(error=str(e))
        return self.json_response("", status_code=httplib.NO_CONTENT)


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
