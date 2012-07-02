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
from libcloud.test.dns.test_zerigo import ZerigoMockHttp

from libcloud_rest.api.versions import versions as rest_versions
from libcloud_rest.application import LibcloudRestApp
from libcloud_rest.exception import LibcloudError, ValidationError
from tests.file_fixtures import DNSFixtures


class ZerigoTests(unittest2.TestCase):
    def setUp(self):
        self.url_tmpl = rest_versions[libcloud.__version__] +\
            '/dns/ZERIGO/%s?test=1'
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = DNSFixtures('zerigo')
        self.headers = {'x-auth-user': 'email', 'x-api-key': 'api token'}
        ZerigoMockHttp.type = None

    def test_create_zone_success(self):
        ZerigoMockHttp.type = 'CREATE_ZONE'
        url = self.url_tmpl % ('zones')
        test_request = self.fixtures.load('create_zone_valid.json')
        test_request_json = json.loads(test_request)
        resp = self.client.post(url,
                                headers=self.headers,
                                data=json.dumps(test_request_json),
                                content_type='application/json')
        zone = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.CREATED)
        self.assertEqual(zone['id'], '12345679')
        self.assertEqual(zone['domain'], 'foo.bar.com')

    def test_create_zone_libcloud_error(self):
        ZerigoMockHttp.type = 'CREATE_ZONE_VALIDATION_ERROR'
        url = self.url_tmpl % ('zones')
        test_request = self.fixtures.load('create_zone_bad_ttl.json')
        test_request_json = json.loads(test_request)
        resp = self.client.post(url,
                                headers=self.headers,
                                data=json.dumps(test_request_json),
                                content_type='application/json')
        resp_data = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.INTERNAL_SERVER_ERROR)
        self.assertEqual(resp_data['error']['code'], LibcloudError.code)

    def test_create_zone_validation_error(self):
        url = self.url_tmpl % ('zones')
        test_request = self.fixtures.load('create_zone_invalid.json')
        test_request_json = json.loads(test_request)
        resp = self.client.post(url,
                                headers=self.headers,
                                data=json.dumps(test_request_json),
                                content_type='application/json')
        resp_data = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.BAD_REQUEST)
        self.assertEqual(resp_data['error']['code'], ValidationError.code)

    def test_update_zone_success(self):
        ZerigoMockHttp.type = None
        url = self.url_tmpl % ('zones')
        zones_resp = self.client.get(url, headers=self.headers)
        zones_resp_data = json.loads(zones_resp.data)
        zone = zones_resp_data[0]
        url = self.url_tmpl % ('/'.join(['zones', zone['id']]))
        resp = self.client.put(url, headers=self.headers,
                               data='{"ttl": 10}',
                               content_type='application/json')
        updated_zone = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertEqual(updated_zone['id'], zone['id'])
        self.assertEqual(updated_zone['domain'], 'example.com')
        self.assertEqual(updated_zone['type'], zone['type'])
        self.assertEqual(updated_zone['ttl'], 10)


if __name__ == '__main__':
    import tests
    sys.exit(unittest2.main())
