# -*- coding:utf-8 -*-
import unittest2
import mock
from libcloud.compute.drivers.dummy import DummyNodeDriver
from libcloud.compute.base import Node

from libcloud_rest.api import handlers
from libcloud_rest.exception import InternalError, LibcloudError,\
    MalformedJSONError, ValidationError
from libcloud_rest.api import validators as valid


class TestHandlers(unittest2.TestCase):
    def setUp(self):
        self.base_handler = handlers.BaseServiceHandler()
        self.base_handler._get_driver_instance = \
            mock.MagicMock(return_value=DummyNodeDriver(2))

    def test_execute_driver_method(self):
        self.assertRaises(InternalError,
                          self.base_handler._execute_driver_method, 'bad_name')
        self.assertRaises(LibcloudError,
                          self.base_handler._execute_driver_method,
                          'list_nodes', 'arg1')
        node = self.base_handler._execute_driver_method('list_nodes')[0]
        self.assertTrue(isinstance(node, Node))

    def test_load_json(self):
        validator = valid.DictValidator({
            'name': valid.StringValidator(),
        })
        malformed_json = "{ '1'}"
        self.assertRaises(MalformedJSONError, self.base_handler._load_json,
                          malformed_json)
        invalid_data = '{"a": "a"}'
        #without validator
        self.assertTrue(self.base_handler._load_json(invalid_data))
        #with validator
        self.assertRaises(ValidationError, self.base_handler._load_json,
                          invalid_data, validator)
        valid_data = '{"name": "a"}'
        self.assertTrue(self.base_handler._load_json(valid_data, validator))
