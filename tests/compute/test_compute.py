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


class ComputeTest(unittest2.TestCase):
    def setUp(self):
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = FileFixtures('compute')

    def test_list_providers(self):
        url = rest_versions[libcloud.__version__] + '/compute/providers'
        resp = self.client.get(url)
        data = json.loads(self.fixtures.load('providers.json'))
        resp_data = json.loads(resp.data)
        self.assertItemsEqual(data['providers'], resp_data['providers'])
        self.assertEqual(resp.status, '200 OK')

if __name__ == '__main__':
    sys.exit(unittest2.main())
