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
