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
from libcloud.dns.types import RecordType
from test.dns.test_rackspace import RackspaceMockHttp

from libcloud_rest.api.versions import versions as rest_versions
from libcloud_rest.application import LibcloudRestApp
from libcloud_rest.exception import LibcloudError
from tests.file_fixtures import DNSFixtures


class RackspaceUSTests(unittest2.TestCase):
    def setUp(self):
        self.url_tmpl = rest_versions[libcloud.__version__] +\
                        '/dns/RACKSPACE_US/%s?test=1'
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = DNSFixtures('rackspace_us')
        self.headers = {'x-auth-user': 'user', 'x-api-key': 'key'}
        RackspaceMockHttp.type = None

    def test_list_zones(self):
        url = self.url_tmpl % 'zones'
        resp = self.client.get(url, headers=self.headers)
        zones = json.loads(resp.data)
        self.assertEqual(len(zones), 6)
        self.assertEqual(zones[0]['domain'], 'foo4.bar.com')
        self.assertEqual(resp.status_code, httplib.OK)

    def test_list_zones_not_successful(self):
        RackspaceMockHttp.type = '413'
        url = self.url_tmpl % 'zones'
        resp = self.client.get(url, headers=self.headers)
        resp_data = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.INTERNAL_SERVER_ERROR)
        self.assertEqual(resp_data['error']['code'], LibcloudError.code)

    def test_list_zones_no_result(self):
        RackspaceMockHttp.type = 'NO_RESULTS'
        url = self.url_tmpl % 'zones'
        resp = self.client.get(url, headers=self.headers)
        zones = json.loads(resp.data)
        self.assertEqual(len(zones), 0)
        self.assertEqual(resp.status_code, httplib.OK)

    def test_list_records_success(self):
        url = self.url_tmpl % 'zones'
        zones_resp = self.client.get(url, headers=self.headers)
        zones_resp_data = json.loads(zones_resp.data)
        zone_id = zones_resp_data[0]['id']
        url = self.url_tmpl % '/'.join(['zones', str(zone_id), 'records'])
        resp = self.client.get(url, headers=self.headers)
        records = json.loads(resp.data)
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]['name'], 'test3')
        self.assertEqual(records[0]['type'], RecordType.A)
        self.assertEqual(records[0]['data'], '127.7.7.7')
        self.assertEqual(resp.status_code, httplib.OK)

    def test_list_records_zone_does_not_exist(self):
        url = self.url_tmpl % 'zones'
        zones_resp = self.client.get(url, headers=self.headers)
        zones_resp_data = json.loads(zones_resp.data)
        zone_id = zones_resp_data[0]['id']
        RackspaceMockHttp.type = 'ZONE_DOES_NOT_EXIST'
        url = self.url_tmpl % '/'.join(['zones', str(zone_id), 'records'])
        resp = self.client.get(url, headers=self.headers)
        resp_data = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.INTERNAL_SERVER_ERROR)
        self.assertEqual(resp_data['error']['code'], LibcloudError.code)


if __name__ == '__main__':
    import tests
    sys.exit(unittest2.main())
