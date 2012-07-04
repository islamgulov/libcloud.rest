# -*- coding:utf-8 -*-
import unittest2

from libcloud_rest.api.entries import get_entry
from libcloud_rest.exception import MalformedJSONError, ValidationError


class StringEntryTests(unittest2.TestCase):
    def setUp(self):
        self.entry = get_entry('zone_id', 'C{str}',
                               '"ID of the zone which is required')

    def test_validate(self):
        valid_json = '{"zone_id": "123"}'
        self.entry.validate(valid_json)
        malformed_json = "{ '1'}"
        self.assertRaises(MalformedJSONError, self.entry.validate,
                          malformed_json)
        invalid_json = '{"zone_id": 123}'
        self.assertRaises(ValidationError, self.entry.validate, invalid_json)
