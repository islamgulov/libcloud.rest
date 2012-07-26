# -*- coding:utf-8 -*-
import inspect
from itertools import chain

from libcloud_rest.errors import ValidationError, MissingArguments,\
    UnknownArgument


class BaseValidator(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.configure(args, kwargs)

    def configure(self, args, kwargs):
        self.required = kwargs.pop('required', True)
        self.default_name = kwargs.pop('default_name', 'Data')
        self._name = kwargs.pop('name', None)

    def _get_name(self):
        if self._name is not None:
            return self._name
        return self.default_name

    def _set_name(self, new_name):
        self._name = new_name

    name = property(_get_name, _set_name)

    def __call__(self, data):
        """
        Validate data
        @return True if data correct
        """
        self.raw_data = data
        self._validate()
        return True

    def _validate(self):
        if not self.required and not self.raw_data:
            return True
        self._check_data()

    def _check_data(self):
        """
        Validation function that does not check required flag.
        """
        raise NotImplemented('To use this class inherit from it '
                             'and define _check_data method')


class NumericValidator(BaseValidator):
    numeric_type = None

    def configure(self, args, kwargs):
        self.max = kwargs.pop('max', None)
        self.min = kwargs.pop('min', None)
        super(NumericValidator, self).configure(args, kwargs)

    def _check_data(self):
        try:
            i = self.numeric_type(self.raw_data)
        except (ValueError, TypeError):
            raise ValidationError('%s must be integer' % (self.name))
        if self.max is not None and i > self.max:
            raise ValidationError('%s must be smaller than %i' % (self.name,
                                                                  self.max))
        if self.max is not None and i < self.min:
            raise ValidationError('%s must be larger than %i' % (self.name,
                                                                 self.min))


class IntegerValidator(NumericValidator):
    numeric_type = int


class FloatValidator(NumericValidator):
    numeric_type = float


class StringValidator(BaseValidator):
    def _check_data(self):
        if not isinstance(self.raw_data, basestring):
            raise ValidationError('%s must be string' % (self.name))


class BooleanValidator(BaseValidator):
    def _check_data(self):
        return bool(self.raw_data)


class NoneValidator(BaseValidator):
    def _check_data(self):
        return self.raw_data is None


class ConstValidator(BaseValidator):
    def configure(self, args, kwargs):
        self.const = args[0]
        super(ConstValidator, self).configure(args, kwargs)

    def _check_data(self):
        if self.const != self.raw_data:
            raise ValidationError('%s must be equal to %s' % (self.name,
                                                              str(self.const)))


class DictValidator(BaseValidator):
    def configure(self, args, kwargs):
        if not isinstance(args[0], dict):
            raise TypeError('Argument must be dict')
        self.items_validators = args[0]
        for key, validator in self.items_validators.iteritems():
            if validator.name == validator.default_name:
                validator.name = key
        super(DictValidator, self).configure(args, kwargs)

    def _check_data(self):
        if not isinstance(self.raw_data, dict):
            raise ValidationError('%s must be dict' % (self.name))
        for key, validator in self.items_validators.iteritems():
            validator(self.raw_data.get(key, None))
