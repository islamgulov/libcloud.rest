# -*- coding:utf-8 -*-
import unittest2

from libcloud_rest.api import validators
from libcloud_rest.exception import ValidationError


class TestParser(unittest2.TestCase):
    def test_string(self):
        string_validator = validators.StringValidator()
        valid_string = 'abc'
        invalid_type = 123
        self.assertTrue(string_validator(valid_string))
        self.assertRaises(ValidationError, string_validator, invalid_type)

    def test_integer(self):
        integer_validator = validators.IntegerValidator()
        valid_integer = 123
        valid_integer2 = 12.3
        invalid_integer = '12.3'
        self.assertTrue(integer_validator(valid_integer))
        self.assertTrue(integer_validator(valid_integer2))
        self.assertRaises(ValidationError, integer_validator, invalid_integer)

    def test_dict(self):
        dict_validator = validators.DictValidator(
                {'arg1': validators.StringValidator()})
        valid_dict = {'arg1': 'str'}
        invalid_dict = {'arg1': 123}
        invalid_dict2 = {'abc': 'str'}
        self.assertTrue(dict_validator(valid_dict))
        self.assertRaises(ValidationError, dict_validator, invalid_dict)
        self.assertRaises(ValidationError, dict_validator, invalid_dict2)

    def test_required(self):
        req_string_validator = validators.StringValidator()
        not_req_string_validator = validators.StringValidator(required=False)
        dict_validator = validators.DictValidator({
            'req': req_string_validator,
            'opt': not_req_string_validator,
            })
        valid_dict = {'req': 'abc'}
        valid_dict2 = {'req': 'abc', 'opt': 'def'}
        invalid_dict = {'opt': 'def'}
        self.assertTrue(dict_validator(valid_dict))
        self.assertTrue(dict_validator(valid_dict2))
        self.assertRaises(ValidationError, dict_validator, invalid_dict)
