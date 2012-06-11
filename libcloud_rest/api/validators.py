# -*- coding:utf-8 -*-
from libcloud_rest.errors import MissingHeaderError
from libcloud_rest.api.parser import ARGS_TO_XHEADERS_DICT
from libcloud_rest.exception import ValidationError

__all__ = [
    'validate_header_arguments',
    ]


def validate_header_arguments(required_arguments, arguments):
    """
    Validate that in all required arguments are existing.
    @param required_arguments:
    @param arguments:

    @raise: L{MissingHeaderError}
    """
    for arg_altertives in required_arguments:
        if not any([arg in arguments for arg in arg_altertives]):
            header_names = [ARGS_TO_XHEADERS_DICT[arg]
                            for arg in arg_altertives]
            raise MissingHeaderError(header=' or '.join(header_names))


class BaseValidator(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.required = kwargs.pop('required', True)

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


class IntegerValidator(BaseValidator):
    def _check_data(self):
        try:
            _ = int(self.raw_data)
        except (ValueError, TypeError):
            raise ValidationError('Data must be integer')


class StringValidator(BaseValidator):
    def _check_data(self):
        if not isinstance(self.raw_data, basestring):
            raise ValidationError('Data must be string')


class DictValidator(BaseValidator):

    def __init__(self, *args, **kwargs):
        print args[0]
        if not isinstance(args[0], dict):
            raise TypeError('Argument must be dict')
        self.items_validators = args[0]
        super(DictValidator, self).__init__(args, kwargs)

    def _check_data(self):
        if not isinstance(self.raw_data, dict):
            raise ValidationError('Data must be dict')
        for key, validator in self.items_validators.iteritems():
            validator(self.raw_data.get(key, None))
