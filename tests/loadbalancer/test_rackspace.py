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
from libcloud.loadbalancer.base import Algorithm
from libcloud.loadbalancer.types import MemberCondition
from libcloud.test.loadbalancer.test_rackspace import RackspaceLBMockHttp

from libcloud_rest.api.versions import versions as rest_versions
from libcloud_rest.application import LibcloudRestApp
from tests.file_fixtures import DNSFixtures


class RackspaceUSTests(unittest2.TestCase):
    def setUp(self):
        self.url_tmpl = rest_versions[libcloud.__version__] +\
            '/loadbalancer/RACKSPACE_US/%s?test=1'
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.fixtures = DNSFixtures('rackspace_us')
        self.headers = {'x-auth-user': 'user', 'x-api-key': 'key'}
        RackspaceLBMockHttp.type = None

    def test_list_protocols(self):
        url = self.url_tmpl % ('protocols')
        resp = self.client.get(url, headers=self.headers)
        protocols = json.loads(resp.data)
        self.assertEqual(len(protocols), 10)
        self.assertIn('http', protocols)
        self.assertEqual(resp.status_code, httplib.OK)

    def test_ex_list_protocols_with_default_ports(self):
        url = self.url_tmpl % ('ex_list_protocols_with_default_ports')
        resp = self.client.post(url, headers=self.headers,
                                content_type='application/json')
        protocols = json.loads(resp.data)
        self.assertEqual(len(protocols), 10)
        self.assertIn(['http', 80], protocols)
        self.assertEqual(resp.status_code, httplib.OK)

    def test_list_supported_algorithms(self):
        url = self.url_tmpl % ('algorithms')
        resp = self.client.get(url, headers=self.headers)
        algorithms = json.loads(resp.data)
        self.assertTrue(Algorithm.RANDOM in algorithms)
        self.assertTrue(Algorithm.ROUND_ROBIN in algorithms)
        self.assertTrue(Algorithm.LEAST_CONNECTIONS in algorithms)
        self.assertTrue(Algorithm.WEIGHTED_ROUND_ROBIN in algorithms)
        self.assertTrue(Algorithm.WEIGHTED_LEAST_CONNECTIONS in algorithms)
        self.assertEqual(resp.status_code, httplib.OK)

    def test_ex_list_algorithms(self):
        url = self.url_tmpl % ('ex_list_algorithm_names')
        resp = self.client.post(url, headers=self.headers,
                                content_type='application/json')
        algorithms = json.loads(resp.data)
        self.assertIn("RANDOM", algorithms)
        self.assertIn("ROUND_ROBIN", algorithms)
        self.assertIn("LEAST_CONNECTIONS", algorithms)
        self.assertIn("WEIGHTED_ROUND_ROBIN", algorithms)
        self.assertIn("WEIGHTED_LEAST_CONNECTIONS", algorithms)
        self.assertEqual(resp.status_code, httplib.OK)

    def test_list_balancers(self):
        url = self.url_tmpl % ('balancers')
        resp = self.client.get(url, headers=self.headers)
        balancers = json.loads(resp.data)
        self.assertEquals(len(balancers), 2)
        self.assertEquals(balancers[0]['name'], "test0")
        self.assertEquals(balancers[0]['id'], "8155")
        self.assertEquals(balancers[0]['port'], 80)
        self.assertEquals(balancers[0]['ip'], "1.1.1.25")
        self.assertEquals(balancers[1]['name'], "test1")
        self.assertEquals(balancers[1]['id'], "8156")
        self.assertEqual(resp.status_code, httplib.OK)

    def test_list_balancers_ex_member_address(self):
        RackspaceLBMockHttp.type = 'EX_MEMBER_ADDRESS'
        url = rest_versions[libcloud.__version__] +\
            '/loadbalancer/RACKSPACE_US/balancers'
        resp = self.client.get(url, headers=self.headers,
                               query_string={'ex_member_address': '127.0.0.1',
                                             'test': 1})
        balancers = json.loads(resp.data)

        self.assertEquals(len(balancers), 3)
        self.assertEquals(balancers[0]['name'], 'First Loadbalancer')
        self.assertEquals(balancers[0]['id'], '1')
        self.assertEquals(balancers[1]['name'], 'Second Loadbalancer')
        self.assertEquals(balancers[1]['id'], '2')
        self.assertEquals(balancers[2]['name'], 'Third Loadbalancer')
        self.assertEquals(balancers[2]['id'], '8')
        self.assertEqual(resp.status_code, httplib.OK)

    def test_create_node(self):
        url = self.url_tmpl % ('balancers')
        RackspaceLBMockHttp.type = None
        request_data = {
            'name': 'test2',
            'port': '80',
            'members': [{'member_id': '',
                         'member_ip': '10.1.0.10',
                         'member_port': 80,
                         'member_extra':{'condition': MemberCondition.DISABLED,
                                         'weight': 10}},
                        {'member_id': '',
                         'member_ip': '10.1.0.11',
                         'member_port': 80}, ],
            'algorithm': 'ROUND_ROBIN',
        }
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(request_data),
                                content_type='application/json')
        self.assertEqual(resp.status_code, httplib.CREATED)
        self.assertEqual(resp.headers.get('Location'), '8290')
        balancer = json.loads(resp.data)
        self.assertEqual(balancer['name'], 'test2')

    def test_destroy_balancer(self):
        url = self.url_tmpl % ('balancers')
        resp = self.client.get(url, headers=self.headers)
        balancer = json.loads(resp.data)[0]
        url = self.url_tmpl % ('/'.join(['balancers', balancer['id']]))
        resp = self.client.delete(url, headers=self.headers)
        self.assertEqual(resp.status_code, httplib.ACCEPTED)

    def test_update_balancer_protocols(self):
        url = self.url_tmpl % ('/'.join(['balancers', '3130']))
        request_data = {'protocol': 'HTTPS'}
        resp = self.client.put(url, headers=self.headers,
                               data=json.dumps(request_data),
                               content_type='application/json')
        self.assertEqual(resp.status_code, httplib.OK)

    def test_update_balancer_port(self):
        url = self.url_tmpl % ('/'.join(['balancers', '3131']))
        request_data = {'port': 1337}
        resp = self.client.put(url, headers=self.headers,
                               data=json.dumps(request_data),
                               content_type='application/json')
        balancer = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertEqual(balancer['port'], 1337)

    def test_update_balancer_name(self):
        url = self.url_tmpl % ('/'.join(['balancers', '3132']))
        request_data = {'name': 'new_lb_name'}
        resp = self.client.put(url, headers=self.headers,
                               data=json.dumps(request_data),
                               content_type='application/json')
        balancer = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertEqual(balancer['name'], 'new_lb_name')

    def test_get_balancer(self):
        url = self.url_tmpl % ('/'.join(['balancers', '8290']))
        resp = self.client.get(url, headers=self.headers)
        balancer = json.loads(resp.data)
        self.assertEquals(balancer['name'], 'test2')
        self.assertEquals(balancer['id'], '8290')
        self.assertEqual(resp.status_code, httplib.OK)
