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
from tests.file_fixtures import ComputeFixtures


class CloudstackTests(unittest2.TestCase):
    def setUp(self):
        self.url_tmpl = rest_versions[libcloud.__version__] +\
                        '/compute/cloudstack/%s?test=1'
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = ComputeFixtures('cloudstack')

    def test_list_nodes(self):
        url = self.url_tmpl % 'nodes'
        headers = {'x-auth-user': 'apikey', 'x-api-key': 'secret',
                   'x-provider-path': '/test/path',
                   'x-provider-host': 'api.dummy.com'}
        resp = self.client.get(url, headers=headers)
        resp_data = json.loads(resp.data)
        test_data = json.loads(self.fixtures.load('list_nodes.json'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp_data, test_data)

    def test_bad_headers(self):
        url = self.url_tmpl % 'nodes'
        headers = {'x-auth-user': 'apikey'}
        resp = self.client.get(url, headers=headers)
        self.assertEqual(resp.status_code, 400)


if __name__ == '__main__':
    sys.exit(unittest2.main())
