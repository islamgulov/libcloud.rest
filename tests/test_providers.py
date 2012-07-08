# -*- coding:utf-8 -*-
import unittest2

from libcloud_rest.api.providers import DriverMethod
from libcloud_rest.utils import json


class FakeDriver(object):
    def fake_method(self, node, volume, device='/deb/sdb', extra={}):
        '''
        teachess volume to node.

        @param      node: Node to attach volume to
        @type       node: L{Node}

        @param      volume: Volume to attach
        @type       volume: C{str}

        @param      device: Where the device is exposed,
                            e.g. '/dev/sdb (required)
        @type       device: C{str}

        @param extra: Extra attributes (driver specific).
        @type extra: C{dict}

        @return: C{str}
        '''
        pass


class Tests(unittest2.TestCase):
    def setUp(self):
        self.driver_method = DriverMethod(FakeDriver, 'fake_method')

    def test_get_description(self):
        description = self.driver_method.get_description()
        data = json.loads(description)
        self.assertEqual('fake_method', data['name'])
        self.assertEqual('teachess volume to node.', data['description'])
        arguments = data['arguments']
        test_args = [{'required': True, 'type': 'string', 'name': 'node_id',
                      'description': 'ID of the node which should be used'},
                     {'required': True, 'type': 'string', 'name': 'volume',
                     'description': 'Volume to attach'},
                     {'required': True, 'type': 'string', 'name': 'device',
                      'description': "Where the device is exposed,\n"
                                     "e.g. '/dev/sdb (required)"},
                     {'required': False, 'type': 'dictionary', 'name': 'extra',
                      'description': 'Extra attributes (driver specific).',
                      'default': {}}
                     ]
        self.assertItemsEqual(test_args, arguments)


if __name__ == '__main__':
    unittest2.main()
