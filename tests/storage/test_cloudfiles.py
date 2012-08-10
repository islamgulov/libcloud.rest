# -*- coding:utf-8 -*-
from __future__ import with_statement
import unittest2
import httplib

try:
    import simplejson as json
except ImportError:
    import json

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
import libcloud
from libcloud.test.storage.test_cloudfiles import CloudFilesMockHttp,\
    CloudFilesMockRawResponse

from libcloud_rest.api.versions import versions as rest_versions
from libcloud_rest.application import LibcloudRestApp
from tests.file_fixtures import DNSFixtures


class RackspaceUSTests(unittest2.TestCase):
    def setUp(self):
        self.url_tmpl = rest_versions[libcloud.__version__] +\
            '/storage/CLOUDFILES_US/%s?test=1'
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.headers = {'x-auth-user': 'user', 'x-api-key': 'key'}
        CloudFilesMockHttp.type = None
        CloudFilesMockRawResponse.type = None

    def test_list_containers(self):
        CloudFilesMockHttp.type = 'EMPTY'
        url = self.url_tmpl % ('containers')
        resp = self.client.get(url, headers=self.headers)
        containers = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertEqual(len(containers), 0)

        CloudFilesMockHttp.type = None
        url = self.url_tmpl % ('containers')
        resp = self.client.get(url, headers=self.headers)
        containers = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertEqual(len(containers), 3)

        container = [c for c in containers if c['name'] == 'container2'][0]
        self.assertEqual(container['extra']['object_count'], 120)
        self.assertEqual(container['extra']['size'], 340084450)
