# -*- coding:utf-8 -*-
import unittest2

try:
    import simplejson as json
except ImportError:
    import json

from libcloud.compute.base import Node, NodeState,\
    NodeAuthPassword, NodeAuthSSHKey
from libcloud.compute.drivers.cloudstack import CloudStackNodeDriver
from libcloud.dns.types import RecordType

from libcloud_rest.api.entries import Entry, LibcloudObjectEntry, StringField,\
    ListEntry
from libcloud_rest.errors import MalformedJSONError, ValidationError,\
    NoSuchObjectError, MissingArguments, TooManyArgumentsError
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
        self.assertEqual(argument['type'], 'str')

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
    object_class = FakeObject
    type_name = 'L{Fake}'
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
        self.entry = FakeEntry('fake', 'L{Fake}', 'just for test', True)

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
        get_arg = lambda name: [arg for arg in args
                                if arg['name'] == name][0]
        fake_id_arg = get_arg('fake_id')
        self.assertEqual(fake_id_arg['type'], 'str')
        fake_name_arg = get_arg('fake_name')
        self.assertEqual(fake_name_arg['type'], 'str')


class FakeDefaultEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = FakeEntry('fake', 'L{Fake}', 'just for test', True,
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
        get_arg = lambda name: [arg for arg in args
                                if arg['name'] == name][0]
        fake_id_arg = get_arg('fake_id')
        self.assertEqual(fake_id_arg['type'], 'str')
        fake_name_arg = get_arg('fake_name')
        self.assertEqual(fake_name_arg['type'], 'str')


class NodeEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = Entry('node', 'L{Node}',
                           'node which is required')

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
        self.assertEqual(argument['type'], 'str')

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
        node = self.entry.from_json(json_data, None)
        self.assertEqual(node.id, '2600')


class OneOfEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = Entry('node',
                           'L{NodeAuthSSHKey} or L{NodeAuthPassword}',
                           'Initial authentication information for the node')

    def test_get_arguments(self):
        args = self.entry.get_arguments()
        self.assertEqual(2, len(args))
        get_arg = lambda name: [arg for arg in args
                                if arg['name'] == name][0]
        node_pubkey_arg = get_arg('node_pubkey')
        self.assertEqual(node_pubkey_arg['type'], 'str')
        node_password_arg = get_arg('node_password')
        self.assertEqual(node_password_arg['type'], 'str')

    def test_from_json(self):
        key_json = '{"node_pubkey": "123", "unknown_arg": 123}'
        node_auth_ssh_key = self.entry.from_json(key_json, None)
        self.assertEqual("123", node_auth_ssh_key.pubkey)
        password_json = '{"node_password": "321", "unknown_arg": 123}'
        node_auth_password = self.entry.from_json(password_json, None)
        self.assertEqual("321", node_auth_password.password)
        key_password_json = '{"node_pubkey": "123",'\
                            ' "node_password": "321", "unknown_args": 123}'
        self.assertRaises(TooManyArgumentsError, self.entry.from_json,
                          key_password_json, None)
        empty_json = "{}"
        self.assertRaises(MissingArguments, self.entry.from_json,
                          empty_json, None)
        invalid_json = '{"node_pubkey": 123}'
        self.assertRaises(ValidationError, self.entry.from_json,
                          invalid_json, None)

    def test_to_json(self):
        node_ssh_key = NodeAuthSSHKey('pk')
        self.assertEqual('{"pubkey": "pk"}', self.entry.to_json(node_ssh_key))
        node_password = NodeAuthPassword('pwd')
        self.assertEqual('{"password": "pwd"}',
                         self.entry.to_json(node_password))


class DefaultOneOfEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = Entry('attr', 'C{str} or C{dict}',
                           'Test description',
                           default='default_value')

    def test_get_arguments(self):
        args = self.entry.get_arguments()
        self.assertEqual(2, len(args))
        test_args = [{'type': 'str', 'name': 'attr',
                      'description': 'Test description',
                      'required': True},
                     {'type': 'dict', 'name': 'attr',
                      'description': 'Test description',
                      'required': True}]
        self.assertEqual(test_args, args)

    def test_from_json(self):
        str_json = '{"attr": "123", "unknown_arg": 123}'
        self.assertEqual("123", self.entry.from_json(str_json, None))
        dict_json = '{"attr": "{}", "unknown_arg": 123}'
        self.assertEqual("{}", self.entry.from_json(dict_json, None))
        invalid_json = '{"attr": 555}'
        self.assertRaises(ValidationError, self.entry.from_json,
                          invalid_json, None)
        without_attr_json = '{"unknown_arg": 123}'
        self.assertEqual('default_value',
                         self.entry.from_json(without_attr_json, None))
        malformed_json = '{'
        self.assertRaises(MalformedJSONError, self.entry.from_json,
                          malformed_json, None)

    def test_to_json(self):
        str_data = 'abc'
        self.assertEqual('{"attr": "abc"}', self.entry.to_json(str_data))
        dict_data = {'1': 2}
        self.assertEqual('{"attr": {"1": 2}}', self.entry.to_json(dict_data))
        int_data = 5
        self.assertRaises(ValueError, self.entry.to_json, int_data)


class ListEntryTest(unittest2.TestCase):
    def setUp(self):
        self.entry = ListEntry('result', 'C{list} of L{Node}', 'pass', True)
        self.driver = get_test_driver_instance(CloudStackNodeDriver,
                                               secret='apikey', key='user',
                                               host='api.dummy.com',
                                               path='/test/path')

    def test_to_json(self):
        n1 = Node('id1', 'test1', NodeState.RUNNING, None, None, None)
        n1_json_data = {"public_ips": [], "state": 0,
                        "id": "id1", "name": "test1"}
        n2 = Node('id2', 'test2', NodeState.PENDING, None, None, None)
        n2_json_data = {"public_ips": [], "state": 3,
                        "id": "id2", "name": "test2"}
        self.assertItemsEqual([n1_json_data, n2_json_data],
                              json.loads(self.entry.to_json([n1, n2])))

    def test_from_json(self):
        nodes = '{"result": [{"node_id": "2600"}, {"node_id": "2601"}]}'
        result = self.entry.from_json(nodes, self.driver)
        get_node = lambda x: [node for node in result if node.id == x][0]
        self.assertTrue(get_node('2600'))
        self.assertTrue(get_node('2601'))


class RecordTypeTest(unittest2.TestCase):
    def setUp(self):
        self.entry = Entry('type', 'L{RecordType}', 'pass', True)

    def test_from_json(self):
        valid_json = '{"record_type": 1}'
        self.assertEqual(self.entry.from_json(valid_json, None),
                         RecordType.AAAA)
        invalid_json = '{"record_type": "ABC"}'
        self.assertRaises(ValidationError, self.entry.from_json,
                          invalid_json, None)
