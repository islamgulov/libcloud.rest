# -*- coding:utf-8 -*-
from __future__ import with_statement
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
from libcloud.dns.base import Zone
from libcloud.test.dns.test_linode import LinodeMockHttp, LinodeDNSDriver
import mock

from libcloud_rest.api.versions import versions as rest_versions
from libcloud_rest.application import LibcloudRestApp
from tests.file_fixtures import DNSFixtures


class LinodeTests(unittest2.TestCase):
    def setUp(self):
        self.url_tmpl = rest_versions[libcloud.__version__] +\
            '/dns/LINODE/%s?test=1'
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = DNSFixtures('linode')
        self.headers = {'x-auth-user': 'user', 'x-api-key': 'key'}
        LinodeMockHttp.use_param = 'api_action'
        LinodeMockHttp.type = None

    def test_create_record_success(self):
        url = self.url_tmpl % ('zones')
        zones_resp = self.client.get(url, headers=self.headers)
        zone_data = json.loads(zones_resp.data)[0]
        zone_id = zone_data['id']
        zone = Zone(zone_id, zone_data['domain'], zone_data['type'],
                    zone_data['ttl'], None)

        url = self.url_tmpl % ('/'.join(['zones', str(zone_id), 'records']))
        request_data = {
            "name": "www",
            "record_type": 0,
            "data": "127.0.0.1"
        }
        with mock.patch.object(LinodeDNSDriver, 'get_zone',
                               mocksignature=True) as get_zone_mock:
            get_zone_mock.return_value = zone
            resp = self.client.post(url, headers=self.headers,
                                    data=json.dumps(request_data),
                                    content_type='application/json')
        record = json.loads(resp.data)

        self.assertEqual(record['id'], '28537')
        self.assertEqual(record['name'], 'www')
        self.assertEqual(record['type'], RecordType.A)
        self.assertEqual(record['data'], '127.0.0.1')
        self.assertEqual(resp.status_code, httplib.CREATED)

if __name__ == '__main__':
    import tests
    sys.exit(unittest2.main())
