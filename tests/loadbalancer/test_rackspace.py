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
from libcloud.loadbalancer.drivers.rackspace import RackspaceAccessRuleType
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
            'algorithm': Algorithm.ROUND_ROBIN,
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

    def test_get_balancer_extra_vips(self):
        url = self.url_tmpl % ('/'.join(['balancers', '18940']))
        resp = self.client.get(url, headers=self.headers)
        balancer = json.loads(resp.data)
        self.assertEquals(
            balancer['extra']['virtualIps'], [{'address':'50.56.49.149',
                                               'id':2359,
                                               'type':'PUBLIC',
                                               'ipVersion':'IPV4'}])

    def test_get_balancer_connect_health_monitor(self):
        url = self.url_tmpl % ('/'.join(['balancers', '94695']))
        resp = self.client.get(url, headers=self.headers)
        balancer = json.loads(resp.data)
        balancer_health_monitor = balancer['extra']["healthMonitor"]
        self.assertEquals(balancer_health_monitor['type'], 'CONNECT')
        self.assertEquals(balancer_health_monitor['delay'], 10)
        self.assertEquals(balancer_health_monitor['timeout'], 5)
        self.assertEquals(balancer_health_monitor[
                          'attempts_before_deactivation'], 2)

    def test_get_balancer_connection_throttle(self):
        url = self.url_tmpl % ('/'.join(['balancers', '94695']))
        resp = self.client.get(url, headers=self.headers)
        balancer = json.loads(resp.data)
        balancer_connection_throttle = balancer['extra']["connectionThrottle"]
        self.assertEquals(
            balancer_connection_throttle['min_connections'], 50)
        self.assertEquals(
            balancer_connection_throttle['max_connections'], 200)
        self.assertEquals(
            balancer_connection_throttle['max_connection_rate'], 50)
        self.assertEquals(
            balancer_connection_throttle['rate_interval_seconds'], 10)
        self.assertEqual(resp.status_code, httplib.OK)

    def test_get_access_list(self):
        url = self.url_tmpl % ('/'.join(['balancers', '18940']))
        resp = self.client.get(url, headers=self.headers)
        balancer_id = json.loads(resp.data)['id']
        url = self.url_tmpl % ('ex_balancer_access_list')
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(
                                    {'loadbalancer_id': balancer_id}),
                                content_type='application/json')
        rules = json.loads(resp.data)
        deny_rule, allow_rule = rules
        self.assertEquals(deny_rule['id'], 2883)
        self.assertEquals(
            deny_rule['rule_type'], RackspaceAccessRuleType.DENY)
        self.assertEquals(deny_rule['address'], "0.0.0.0/0")
        self.assertEquals(allow_rule['id'], 2884)
        self.assertEquals(allow_rule['address'], "2001:4801:7901::6/64")
        self.assertEquals(
            allow_rule['rule_type'], RackspaceAccessRuleType.ALLOW)
        self.assertEqual(resp.status_code, httplib.OK)

    def test_ex_create_balancer_access_rule(self):
        request_data = {
            'loadbalancer_id': '94698',
            'rule_type': RackspaceAccessRuleType.DENY,
            'rule_address': '0.0.0.0/0',
        }
        url = self.url_tmpl % ('ex_create_balancer_access_rule')
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(request_data),
                                content_type='application/json')
        rule = json.loads(resp.data)
        self.assertEquals(2883, rule['id'])
        self.assertEqual(resp.status_code, httplib.OK)
