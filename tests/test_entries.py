# -*- coding:utf-8 -*-
import unittest2

from libcloud.compute.base import Node, NodeState

from libcloud_rest.api.entries import get_entry
from libcloud_rest.exception import MalformedJSONError, ValidationError


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


class NodeEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = get_entry('node', 'L{Node}',
                               'node which is required')
        self.node = Node('2006', 'ubu',  NodeState.UNKNOWN,
                         ['1.2.3.4'], Node, Node)

    def test_validate(self):
        valid_json = '{"node_id": "33333"}'
        self.entry.get_json_and_validate(valid_json)
        malformed_json = "{ '1'}"
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
        self.entry.to_json(self.node)
        self.assertRaises(ValueError, self.entry.to_json, ['pass'])
