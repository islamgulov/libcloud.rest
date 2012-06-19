# -*- coding:utf-8 -*-
import sys
import unittest2
import httplib

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


class RackspaceUSTests(unittest2.TestCase):
    def setUp(self):
        self.url_tmpl = rest_versions[libcloud.__version__] +\
                        '/dns/RACKSPACE_US/%s?test=1'
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = ComputeFixtures('rackspace_us')
        self.headers = {'x-auth-user': 'a', 'x-api-key': 'b'}

    def test_list_zones(self):
        url = self.url_tmpl % 'zones'
        resp = self.client.get(url, headers=self.headers)
        zones = json.loads(resp.data)
        self.assertEqual(len(zones), 6)
        self.assertEqual(zones[0]['domain'], 'foo4.bar.com')
        self.assertEqual(resp.status_code, httplib.OK)

if __name__ == '__main__':
    sys.exit(unittest2.main())
