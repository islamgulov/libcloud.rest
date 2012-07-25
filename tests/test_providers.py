# -*- coding:utf-8 -*-
import unittest2

from libcloud_rest.api.providers import DriverMethod
from libcloud_rest.utils import json
from libcloud_rest.errors import MethodParsingException


class FakeDriver(object):
    def ex_create_fake(self, node, volume, device='/deb/sdb',
                       extra={}, varg='value', **kwargs):
        '''
        teachess volume to node.

        @param      node: Node to attach volume to
        @type       node: L{Node}

        @param      volume: Volume to attach
        @type       volume: C{str}

        @param      device: Where the device is exposed,
                            e.g. '/dev/sdb (required)
        @type       device: C{str}

        @param      extra: Extra attributes (driver specific).
        @type       extra: C{dict} or C{str}

        @param      varg: with default value
        @type       varg: C{str}

        @keyword    kwarg: Keyword argument
        @type       kwarg: C{str}

        @return:    return new fake object
        @rtype:     C{str}

        '''
        pass

    def get_not_documented(self):
        pass

    def get_unknown_argument(self, arg, arg2):
        """
        abc
        @param arg: description
        @type arg: C{str}
        @return: C{dict}
        """

    def get_bad_docstring(self, arg):
        """

        @param arg:
        @type arg:
        @return:
        @rtype:
        """

    variable = None


class FakeDriverTests(unittest2.TestCase):
    def setUp(self):
        self.driver_method = DriverMethod(FakeDriver, 'ex_create_fake')

    def test_get_description(self):
        data = self.driver_method.get_description()
        self.assertEqual('ex_create_fake', data['name'])
        self.assertEqual('teachess volume to node.',  data['description'])
        arguments = data['arguments']
        node = {'required': True, 'type': 'str', 'name': 'node_id',
                'description': 'ID of the node which should be used'}
        volume = {'required': True, 'type': 'str', 'name': 'volume',
                  'description': 'Volume to attach'}
        device = {'required': True, 'type': 'str', 'name': 'device',
                  'description': "Where the device is exposed, "
                                 "e.g. '/dev/sdb (required)"}
        extra_dict = {'required': False, 'type': 'dict', 'name': 'extra',
                      'description': 'Extra attributes (driver specific).'}
        extra_str = {'required': False, 'type': 'str', 'name': 'extra',
                     'description': 'Extra attributes (driver specific).'}
        varg = {'default': 'value', 'required': False, 'type': 'str',
                'name': 'varg', 'description': 'with default value'}
        kwarg = {'required': False, 'type': 'str',
                 'name': 'kwarg', 'description': 'Keyword argument'}
        test_args = [node, volume, device, extra_dict, extra_str, varg, kwarg]
        self.assertEqual(arguments, test_args)


class DriverMethodTests(unittest2.TestCase):
    def test_method(self):
        self.assertTrue(DriverMethod(FakeDriver, 'ex_create_fake'))
        self.assertRaises(MethodParsingException, DriverMethod, FakeDriver,
                          'variable')
        self.assertRaises(MethodParsingException, DriverMethod, FakeDriver,
                          'not_documented')
        self.assertRaises(MethodParsingException, DriverMethod, FakeDriver,
                          'unknown_argument')


if __name__ == '__main__':
    unittest2.main()
