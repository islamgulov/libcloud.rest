# -*- coding:utf-8 -*-
import sys
import os
import unittest2

try:
    import simplejson as json
except ImportError:
    import json

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
import libcloud
from test.compute.test_gogrid import GoGridMockHttp

from libcloud_rest.api.versions import versions as rest_versions
from libcloud_rest.application import LibcloudRestApp
from libcloud_rest.exception import UnknownHeadersError, ValidationError, \
    MalformedJSONError
from tests.file_fixtures import ComputeFixtures


class GoGridTests(unittest2.TestCase):
    def setUp(self):
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = ComputeFixtures('gogrid')
        self.headers = {'x-auth-user': 'a', 'x-api-key': 'b'}
        self.url_tmpl = rest_versions[libcloud.__version__] +\
                        '/compute/gogrid/%s?test=1'

    def test_bad_headers(self):
        url = self.url_tmpl % 'nodes'
        headers = {'abs': 1, 'def': 2}
        resp = self.client.get(url, headers=headers)
        self.assertEqual(resp.status_code, 400)

    def test_bad_extra_headers(self):
        url = self.url_tmpl % 'nodes'
        headers = {'x-auth-user': 1, 'x-api-key': 2, 'x-dummy-creds': 3}
        resp = self.client.get(url, headers=headers)
        resp_data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp_data['error']['code'], UnknownHeadersError.code)

    def test_list_nodes(self):
        url = self.url_tmpl % 'nodes'
        resp = self.client.get(url, headers=self.headers)
        resp_data = json.loads(resp.data)
        test_data = json.loads(self.fixtures.load('list_nodes.json'))
        self.assertEqual(resp.status_code, 200)
        self.assertItemsEqual(resp_data, test_data)

    def test_list_sizes(self):
        url = self.url_tmpl % 'sizes'
        resp = self.client.get(url, headers=self.headers)
        resp_data = json.loads(resp.data)
        test_data = json.loads(self.fixtures.load('list_sizes.json'))
        self.assertEqual(resp.status_code, 200)
        self.assertItemsEqual(resp_data, test_data)

    def test_list_images(self):
        url = self.url_tmpl % 'images'
        resp = self.client.get(url, headers=self.headers)
        resp_data = json.loads(resp.data)
        test_data = json.loads(self.fixtures.load('list_images.json'))
        self.assertEqual(resp.status_code, 200)
        self.assertItemsEqual(resp_data, test_data)

    def test_list_locations(self):
        url = self.url_tmpl % 'locations'
        resp = self.client.get(url, headers=self.headers)
        resp_data = json.loads(resp.data)
        test_data = json.loads(self.fixtures.load('list_locations.json'))
        self.assertEqual(resp.status_code, 200)
        self.assertItemsEqual(resp_data, test_data)

    def test_create_node(self):
        url = self.url_tmpl % 'nodes'
        test_request = self.fixtures.load('create_node_request.json')
        test_request_json = json.loads(test_request)
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(test_request_json),
                                content_type='application/json')
        resp_data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp_data['name'], test_request_json['name'])
        self.assertTrue(resp_data['id'] is not None)

    def test_create_node_not_successful(self):
        url = self.url_tmpl % 'nodes'
        test_request = self.fixtures.load('create_node_request_invalid.json')
        test_request_json = json.loads(test_request)
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(test_request_json),
                                content_type='application/json')
        resp_data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp_data['error']['code'], ValidationError.code)

    def test_malformed_json(self):
        url = self.url_tmpl % 'nodes'
        resp = self.client.post(url, headers=self.headers,
                                data="",
                                content_type='application/json')
        resp_data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp_data['error']['code'], MalformedJSONError.code)

    def test_bad_content_type(self):
        url = self.url_tmpl % 'nodes'
        test_request = self.fixtures.load('create_node_request.json')
        test_request_json = json.loads(test_request)
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(test_request_json),
                                content_type='application/xml')
        resp_data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp_data['error']['code'], ValidationError.code)

    def test_bad_content_length(self):
        url = self.url_tmpl % 'nodes'
        content = os.urandom(1000)
        resp = self.client.post(url, headers=self.headers,
                                data=content,
                                content_type='application/json')
        resp_data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp_data['error']['code'], ValidationError.code)

    def test_reboot_node(self):
        node_id = 90967
        url = self.url_tmpl % '/'.join(['nodes', str(node_id), 'reboot'])
        resp = self.client.post(url, headers=self.headers,
                                content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_reboot_node_not_successful(self):
        GoGridMockHttp.type = 'FAIL'
        node_id = 90967
        url = self.url_tmpl % '/'.join(['nodes', str(node_id), 'reboot'])
        resp = self.client.post(url, headers=self.headers,
                                content_type='application/json')
        self.assertEqual(resp.status_code, 500)

    def test_destroy_node(self):
        node_id = 90967
        url = self.url_tmpl % '/'.join(['nodes', str(node_id)])
        resp = self.client.delete(url, headers=self.headers)
        self.assertEqual(resp.status_code, 204)

if __name__ == '__main__':
    sys.exit(unittest2.main())
