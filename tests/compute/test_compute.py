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


class ComputeTest(unittest2.TestCase):
    def setUp(self):
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = ComputeFixtures()

    def test_list_providers(self):
        url = rest_versions[libcloud.__version__] + '/compute/providers'
        resp = self.client.get(url)
        resp_data = json.dumps(json.loads(resp.data), indent=4)
        self.assertEqual(resp.status_code, httplib.OK)

    def test_provider_info(self):
        url = rest_versions[libcloud.__version__] +\
            '/compute/providers/bluebox'
        resp = self.client.get(url)
        resp_data = json.dumps(json.loads(resp.data), indent=4)
        self.assertEqual(resp.status_code, httplib.OK)

if __name__ == '__main__':
    sys.exit(unittest2.main())
