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
from tests.file_fixtures import LoadBalancerFixtures


class LoadBalancerTest(unittest2.TestCase):
    def setUp(self):
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = LoadBalancerFixtures()

    def test_list_providers(self):
        url = rest_versions[libcloud.__version__] + '/loadbalancer/providers'
        resp = self.client.get(url)
        resp_data = json.loads(resp.data)
        provider = {
            "website": "http://www.rackspace.com/",
            "friendly_name": "Rackspace LB",
            "id": "RACKSPACE_US"
        }
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertIn(provider, resp_data)

    def test_provider_info(self):
        url = rest_versions[libcloud.__version__] +\
            '/loadbalancer/providers/RACKSPACE_US'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, httplib.OK)

if __name__ == '__main__':
    sys.exit(unittest2.main())
