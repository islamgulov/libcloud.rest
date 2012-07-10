# -*- coding:utf-8 -*-
import unittest2

from libcloud_rest.api import parser


class TestParser(unittest2.TestCase):
    def test_get_method_requirements(self):
        #valid input
        def t3():
            """
            @requires: x, y or z
            """

        reqs = parser.get_method_requirements(t3)
        self.assertItemsEqual(reqs, [['x'], ['y', 'z']])

        #invalid input
        def t1():
            pass

        self.assertRaises(NotImplementedError,
                          parser.get_method_requirements, t1)

        def t2():
            """
            @return:
            @rtype:
            """

        self.assertRaises(NotImplementedError,
                          parser.get_method_requirements, t2)

    def test_get_docsring(self):
        class A(object):
            def foo(self):
                """docstring"""

            def bar(self):
                pass

        class B(A):
            def foo(self):
                pass

            def bar(self):
                pass

        self.assertEqual(parser.get_method_docstring(B, 'foo'), 'docstring')
        self.assertEqual(parser.get_method_docstring(B, 'bar'), None)

    def test_parse_docstring(self):
        docstring = """
        Return a Zone instance.
        Second line docsting.

        @type zone_id: C{str}
        @param zone_id: Required zone id (required)

        @keyword    auth:   Initial authentication information for the node
                            (optional)
        @type       auth:   L{NodeAuthSSHKey} or L{NodeAuthPassword}

        @return:    instance
        @rtype:     L{Zone} or L{Node}
        """
        description, args, returns = parser.parse_docstring(docstring)
        self.assertTrue(description.startswith('Return'))
        self.assertTrue(description.splitlines()[1].startswith('Second'))
        self.assertEqual(args['zone_id']['type_names'], ['C{str}'])
        self.assertEqual(args['zone_id']['required'], True)
        self.assertEqual(args['auth']['type_names'],
                         ['L{NodeAuthSSHKey}', 'L{NodeAuthPassword}'])
        self.assertEqual(args['auth']['required'], False)
        self.assertEqual(returns, ['L{Zone}', 'L{Node}'])

    def test_parse_docstring_fails(self):
        docstring = """
        Return a Zone instance.
        Second line docsting.

        @type zone_id: C{str}

        @return: L{Zone} or L{Node} instance.
        """
        self.assertRaises(ValueError, parser.parse_docstring, docstring)
        docstring = """
        Return a Zone instance.
        Second line docsting.

        @type zone_id: C{str}
        @param zone_id: Required zone id (required)

        @return: instance.
        """
        self.assertRaises(ValueError, parser.parse_docstring, docstring)

    def test_parse_args(self):
        class A(object):
            def update_zone(self, zone, domain, type='master',
                            ttl=None, extra=None):
                pass

        result = parser.parse_args(A.update_zone)
        self.assertEqual(result.keys(),
                         ['zone', 'domain', 'type', 'ttl', 'extra'])
        self.assertEqual(result['zone']['required'], True)
        self.assertEqual(result['type']['required'], False)
        self.assertFalse('default' in result['zone'])
        self.assertTrue('default' in result['ttl'])
