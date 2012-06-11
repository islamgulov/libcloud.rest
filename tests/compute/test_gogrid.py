# -*- coding:utf-8 -*-
import sys
import unittest2

try:
    import simplejson as json
except ImportError:
    import json

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
import libcloud

from libcloud_rest.api.versions import versions as rest_versions
from libcloud_rest.application import LibcloudRestApp
from tests.file_fixtures import FileFixtures


class GoGridTests(unittest2.TestCase):
    def setUp(self):
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = FileFixtures('compute', 'gogrid')

    def test_list_nodes(self):
        url = rest_versions[libcloud.__version__] +\
              '/compute/gogrid/nodes?test=1'
        headers = {'x-auth-user': 'a', 'x-api-key': 'b'}
        resp = self.client.get(url, headers=headers)
        resp_data = json.loads(resp.data)
        test_data = json.loads(self.fixtures.load('list_nodes.json'))
        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(resp_data, test_data)

    def test_list_sizes(self):
        url = rest_versions[libcloud.__version__] +\
              '/compute/gogrid/sizes?test=1'
        headers = {'x-auth-user': 'a', 'x-api-key': 'b'}
        resp = self.client.get(url, headers=headers)
        resp_data = json.loads(resp.data)
        test_data = json.loads(self.fixtures.load('list_sizes.json'))
        self.assertEqual(resp.status, '200 OK')
        self.assertItemsEqual(resp_data, test_data)

    def test_list_images(self):
        url = rest_versions[libcloud.__version__] +\
              '/compute/gogrid/images?test=1'
        headers = {'x-auth-user': 'a', 'x-api-key': 'b'}
        resp = self.client.get(url, headers=headers)
        resp_data = json.loads(resp.data)
        test_data = json.loads(self.fixtures.load('list_images.json'))
        self.assertEqual(resp.status, '200 OK')
        self.assertItemsEqual(resp_data, test_data)



if __name__ == '__main__':
    sys.exit(unittest2.main())
