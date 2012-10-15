# -*- coding:utf-8 -*-
import httplib
import unittest2

try:
    import simplejson as json
except ImportError:
    import json

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
import libcloud
from libcloud.test.compute.test_openstack import OpenStackMockHttp

from libcloud_rest.api.versions import versions as rest_versions
from libcloud_rest.application import LibcloudRestApp
from tests.file_fixtures import ComputeFixtures


class RackspaceTests(unittest2.TestCase):
    def setUp(self):
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = ComputeFixtures('rackspace')
        self.headers = {'x-auth-user': 'user', 'x-api-key': 'key'}
        self.url_tmpl = rest_versions[libcloud.__version__] +\
            '/compute/RACKSPACE_FIRST_GEN/%s?test=1'
        OpenStackMockHttp.type = None

    def test_create_node(self):
        url = self.url_tmpl % ('nodes')
        test_request = self.fixtures.load('create_node_request.json')
        test_request_json = json.loads(test_request)
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(test_request_json),
                                content_type='application/json')
        node = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.CREATED)
        self.assertEqual(resp.headers.get('Location'), '72258')
        self.assertEqual(node['name'], 'racktest')

    def test_create_node_ex_shared_ip_group(self):
        OpenStackMockHttp.type = 'EX_SHARED_IP_GROUP'
        url = self.url_tmpl % ('nodes')
        test_request = self.fixtures.load('create_node_shared_ip.json')
        test_request_json = json.loads(test_request)
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(test_request_json),
                                content_type='application/json')
        node = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.CREATED)
        self.assertEqual(resp.headers.get('Location'), '72258')
        self.assertEqual(node['name'], 'racktest')
