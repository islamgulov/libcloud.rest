# -*- coding:utf-8 -*-
import unittest2
from libcloud.compute.base import Node, NodeState
from libcloud.compute.drivers.cloudstack import CloudStackNodeDriver

from libcloud_rest.api.entries import LIBCLOUD_TYPES_ENTRIES
from libcloud_rest.exception import NoSuchObjectError, ValidationError
from tests.utils import get_test_driver_instance


class TestNodeEntry(unittest2.TestCase):
    def setUp(self):
        self. entry = LIBCLOUD_TYPES_ENTRIES['L{Node}']
        self.driver = get_test_driver_instance(CloudStackNodeDriver,
                                               secret='apikey', key='user',
                                               host='api.dummy.com',
                                               path='/test/path')

    def test_to_json(self):
        node = Node('111', 'test', NodeState.RUNNING, ['123.123.123.123'],
                    None, Node)
        json_data = self.entry.to_json(node)
        self.assertEqual(node.name, json_data['name'])
        self.assertEqual(node.id, json_data['id'])
        self.assertEqual(node.state, json_data['state'])
        self.assertEqual(node.public_ips, json_data['public_ips'])

    def test_from_json(self):
        json_data = {'node_id': '2600'}
        node = self.entry.from_json(json_data, self.driver,)
        self.assertEqual(node.id, json_data['node_id'])
        bad_json_data = {'node_id': '0062'}
        self.assertRaises(NoSuchObjectError, self.entry.from_json,
                          bad_json_data, self.driver)

    def test_validator(self):
        json_data = {'node_id': '2600', 'unknowd_arg': 123}
        node = self.entry.from_json(json_data, self.driver)
        bad_json_data = {'node': '2600'}
        self.assertRaises(ValidationError, self.entry.from_json,
                          bad_json_data, self.driver)
        bad_json_data = {'node_id': 2600}
        self.assertRaises(ValidationError, self.entry.from_json,
                          bad_json_data, self.driver)


class TestZoneIDEntry(unittest2.TestCase):
    def setUp(self):
        self.entry = LIBCLOUD_TYPES_ENTRIES['zone_id']

    def test_to_json(self):
        zone_id = type('ZoneID', (), {'zone_id': '123'})
        json_data = self.entry.to_json(zone_id)
        self.assertEqual(zone_id.zone_id, json_data['zone_id'])

    def test_from_json(self):
        json_data = {'zone_id': '2600'}
        zone_id = self.entry.from_json(json_data)
        self.assertEqual(zone_id.zone_id, '2600')
