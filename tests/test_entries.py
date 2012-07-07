# -*- coding:utf-8 -*-
import unittest2

try:
    import simplejson as json
except ImportError:
    import json

from libcloud.compute.base import Node, NodeState
from libcloud.compute.drivers.cloudstack import CloudStackNodeDriver

from libcloud_rest.api.entries import Entry, LibcloudObjectEntry, StringField
from libcloud_rest.exception import MalformedJSONError, ValidationError,\
    NoSuchObjectError, MissingArguments
from tests.utils import get_test_driver_instance


class StringEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = Entry('zone_id', 'C{str}',
                           'ID of the zone which is required')

    def test_validate(self):
        valid_json = '{"zone_id": "123"}'
        self.entry._get_json_and_validate(valid_json)
        malformed_json = "{ '1'}"
        self.assertRaises(MalformedJSONError,
                          self.entry._get_json_and_validate,
                          malformed_json)
        invalid_json = '{"zone_id": 123}'
        self.assertRaises(ValidationError,
                          self.entry._get_json_and_validate,
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

    def test_default(self):
        entry = Entry('zone_id', 'C{str}',
                      'ID of the zone which is required',
                      default='12345')
        valid_json = '{"zone_id": "33333", "unknown_arg": 123}'
        self.assertEqual('33333', entry.from_json(valid_json))
        self.assertTrue(entry._get_json_and_validate(valid_json))
        node_json = '{"node_id": "33333", "unknown_arg": 123}'
        self.assertEqual('12345', entry.from_json(node_json))
        self.assertRaises(MissingArguments,
                          entry._get_json_and_validate, node_json)
        valid = '123'
        entry.to_json(valid)
        invalid = 123
        self.assertRaises(ValueError, entry.to_json, invalid)


class FakeObject(object):
    def __init__(self, id, name=''):
        self.id = id
        self.name = name


class FakeEntry(LibcloudObjectEntry):
    render_attrs = ['id', 'name', ]
    fake_id = StringField('Required argument')
    fake_name = StringField('Optional argument', required=False)

    def _get_object(self, json_data, driver):
        args_dict = {'id': json_data['fake_id']}
        if 'fake_name' in json_data:
            args_dict['name'] = json_data['fake_name']
        return FakeObject(**args_dict)


class FakeEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = FakeEntry('fake', 'L{Fake}', 'just for test')

    def test_validate(self):
        valid_json = '{"fake_id": "a", "fake_name": "b", "extra": 1}'
        self.entry._get_json_and_validate(valid_json)
        non_opt_json = '{"fake_id": "a", "fake_name": "b", "extra": 1}'
        self.entry._get_json_and_validate(non_opt_json)
        non_req_json = '{"fake_name": "b", "extra": 1}'
        self.assertRaises(MissingArguments, self.entry._get_json_and_validate,
                          non_req_json)
        invalid_json = '{"fake_id": "a", "fake_name": 555, "extra": 1}'
        self.assertRaises(ValidationError, self.entry._get_json_and_validate,
                          invalid_json)
        malformed_json = '{123}'
        self.assertRaises(MalformedJSONError,
                          self.entry._get_json_and_validate,
                          malformed_json)

    def test_from_json(self):
        valid_data = '{"fake_id": "a", "fake_name": "b", "extra": 5}'
        fake = self.entry.from_json(valid_data, None)
        self.assertEqual('a', fake.id)
        self.assertEqual('b', fake.name)
        valid_data = '{"fake_id": "a", "extra": 5}'
        fake = self.entry.from_json(valid_data, None)
        self.assertEqual('a', fake.id)
        self.assertEqual('', fake.name)
        invalid_data = '{"fake_name": "b", "extra": 5}'
        self.assertRaises(MissingArguments, self.entry.from_json,
                          invalid_data, None)
        empty_json = '{"extra": 1}'
        self.assertRaises(MissingArguments, self.entry.from_json,
                          empty_json, None)

    def test_to_json(self):
        fake = FakeObject('a', 'b')
        json_data = json.loads(self.entry.to_json(fake))
        self.assertEqual('a', json_data['id'])
        self.assertEqual('b', json_data['name'])
        self.assertRaises(ValueError, self.entry.to_json, None)

    def test_get_arguments(self):
        args = self.entry.get_arguments()
        names = [arg['name'] for arg in args]
        self.assertItemsEqual(['fake_id', 'fake_name'], names)
        get_arg = lambda name:  [arg for arg in args
                                 if arg['name'] == name][0]
        fake_id_arg = get_arg('fake_id')
        self.assertEqual(fake_id_arg['type'], 'string')
        self.assertEqual(fake_id_arg['required'], True)
        fake_name_arg = get_arg('fake_name')
        self.assertEqual(fake_name_arg['type'], 'string')
        self.assertEqual(fake_name_arg['required'], False)


class FakeDefaultEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = FakeEntry('fake', 'L{Fake}', 'just for test',
                               default=FakeObject('fid', 'fname'))

    def test_validate(self):
        valid_json = '{"fake_id": "a", "fake_name": "b", "extra": 1}'
        self.entry._get_json_and_validate(valid_json)
        non_opt_json = '{"fake_id": "a", "fake_name": "b", "extra": 1}'
        self.entry._get_json_and_validate(non_opt_json)
        non_req_json = '{"fake_name": "b", "extra": 1}'
        self.assertRaises(MissingArguments, self.entry._get_json_and_validate,
                          non_req_json)
        invalid_json = '{"fake_id": "a", "fake_name": 555, "extra": 1}'
        self.assertRaises(ValidationError, self.entry._get_json_and_validate,
                          invalid_json)
        malformed_json = '{123}'
        self.assertRaises(MalformedJSONError,
                          self.entry._get_json_and_validate,
                          malformed_json)

    def test_from_json(self):
        valid_data = '{"fake_id": "a", "fake_name": "b", "extra": 5}'
        fake = self.entry.from_json(valid_data, None)
        self.assertEqual('a', fake.id)
        self.assertEqual('b', fake.name)
        valid_data = '{"fake_id": "a", "extra": 5}'
        fake = self.entry.from_json(valid_data, None)
        self.assertEqual('a', fake.id)
        self.assertEqual('', fake.name)
        invalid_data = '{"fake_name": "b", "extra": 5}'
        self.assertRaises(MissingArguments, self.entry.from_json,
                          invalid_data, None)
        empty_json = '{"extra": 1}'
        fake = self.entry.from_json(empty_json, None)
        self.assertEqual('fid', fake.id)
        self.assertEqual('fname', fake.name)

    def test_to_json(self):
        fake = FakeObject('a', 'b')
        json_data = json.loads(self.entry.to_json(fake))
        self.assertEqual('a', json_data['id'])
        self.assertEqual('b', json_data['name'])
        self.assertRaises(ValueError, self.entry.to_json, None)

    def test_get_arguments(self):
        args = self.entry.get_arguments()
        names = [arg['name'] for arg in args]
        self.assertItemsEqual(['fake_id', 'fake_name'], names)
        get_arg = lambda name:  [arg for arg in args
                                 if arg['name'] == name][0]
        fake_id_arg = get_arg('fake_id')
        self.assertEqual(fake_id_arg['type'], 'string')
        self.assertEqual(fake_id_arg['required'], True)
        fake_name_arg = get_arg('fake_name')
        self.assertEqual(fake_name_arg['type'], 'string')
        self.assertEqual(fake_name_arg['required'], False)


class NodeEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = Entry('node', 'L{Node}',
                           'node which is required')
        self.driver = get_test_driver_instance(CloudStackNodeDriver,
                                               secret='apikey', key='user',
                                               host='api.dummy.com',
                                               path='/test/path')

    def test_validate(self):
        valid_json = '{"node_id": "33333", "unknown_arg": 123}'
        self.entry._get_json_and_validate(valid_json)
        malformed_json = '{"id"}'
        self.assertRaises(MalformedJSONError,
                          self.entry._get_json_and_validate,
                          malformed_json)
        invalid_json = '{"node_id": 123}'
        self.assertRaises(ValidationError, self.entry._get_json_and_validate,
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
