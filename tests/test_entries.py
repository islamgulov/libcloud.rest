# -*- coding:utf-8 -*-
import unittest2

try:
    import simplejson as json
except ImportError:
    import json

from libcloud.compute.base import Node, NodeState
from libcloud.compute.drivers.cloudstack import CloudStackNodeDriver

from libcloud_rest.api.entries import get_entry
from libcloud_rest.exception import MalformedJSONError, ValidationError,\
    NoSuchObjectError
from tests.utils import get_test_driver_instance


class StringEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = get_entry('zone_id', 'C{str}',
                               'ID of the zone which is required')

    def test_validate(self):
        valid_json = '{"zone_id": "123"}'
        self.entry.get_json_and_validate(valid_json)
        malformed_json = "{ '1'}"
        self.assertRaises(MalformedJSONError, self.entry.get_json_and_validate,
                          malformed_json)
        invalid_json = '{"zone_id": 123}'
        self.assertRaises(ValidationError, self.entry.get_json_and_validate,
                          invalid_json)

    def test_get_arguments(self):
        argument = self.entry.get_arguments()[0]
        self.assertEqual(argument['name'], 'zone_id')
        self.assertEqual(argument['description'],
                         'ID of the zone which is required')
        self.assertEqual(argument['type'], 'string')
        self.assertEqual(argument['required'], True)

    def test_to_json(self):
        valid = '123'
        self.entry.to_json(valid)
        invalid = 123
        self.assertRaises(ValueError, self.entry.to_json, invalid)

    def test_from_json(self):
        valid = '{"zone_id": "123"}'
        self.entry.from_json(valid)
        invalid = '{"zone_id": 333}'
        self.assertRaises(ValidationError, self.entry.from_json, invalid)


class NodeEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = get_entry('node', 'L{Node}',
                               'node which is required')
        self.driver = get_test_driver_instance(CloudStackNodeDriver,
                                               secret='apikey', key='user',
                                               host='api.dummy.com',
                                               path='/test/path')

    def test_validate(self):
        valid_json = '{"node_id": "33333", "unknown_arg": 123}'
        self.entry.get_json_and_validate(valid_json)
        malformed_json = '{"id"}'
        self.assertRaises(MalformedJSONError, self.entry.get_json_and_validate,
                          malformed_json)
        invalid_json = '{"node_id": 123}'
        self.assertRaises(ValidationError, self.entry.get_json_and_validate,
                          invalid_json)

    def test_get_arguments(self):
        argument = self.entry.get_arguments()[0]
        self.assertEqual(argument['name'], 'node_id')
        self.assertEqual(argument['type'], 'string')
        self.assertEqual(argument['required'], True)

    def test_to_json(self):
        node = Node('111', 'test', NodeState.RUNNING, ['123.123.123.123'],
                    None, Node)
        json_data = json.loads(self.entry.to_json(node))
        self.assertEqual(node.name, json_data['name'])
        self.assertEqual(node.id, json_data['id'])
        self.assertEqual(node.state, json_data['state'])
        self.assertEqual(node.public_ips, json_data['public_ips'])
        self.assertRaises(ValueError, self.entry.to_json, ['pass'])

    def test_from_json(self):
        json_data = '{"node_id": "2600"}'
        node = self.entry.from_json(json_data, self.driver)
        self.assertEqual(node.id, '2600')
        bad_json_data = '{"node_id": "0062"}'
        self.assertRaises(NoSuchObjectError, self.entry.from_json,
                          bad_json_data, self.driver)
