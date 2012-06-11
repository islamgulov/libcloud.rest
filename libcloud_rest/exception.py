# -*- coding:utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json


class LibcloudRestError(Exception):
    """
    Base class for other Libcloud REST exceptions.
    To use this class inherit from it and define attributes.
    """

    code = 1000
    name = 'UnknownError'
    message = 'An unknown error occurred.'
    http_status_code = 500

    def __init__(self, **kwargs):
        self.message = self.message % kwargs
        super(LibcloudRestError, self).__init__()

    def to_json(self):
        """

        @return:
        """
        data = {'error':
                        {
                        'code': self.code,
                        'name': self.name,
                        'message': self.message,
                        }
        }
        return json.dumps(data)

    def __str__(self):
        return '%d (%s) - %s' % (self.code, self.name, self.message)


class ProviderNotSupportedError(LibcloudRestError):
    code = 1001
    name = 'ProviderNotSupported'
    message = 'Provider %(provider)s does not supported.'
    http_status_code = 400


class InternalError(LibcloudRestError):
    code = 1002
    name = 'InternalError'
    message = 'We encountered an internal error.'
    http_status_code = 500


class MissingHeaderError(LibcloudRestError):
    code = 1003
    name = 'MissingHeader'
    message = 'Your request was missing a required header: %(header)s.'
    http_status_code = 400


class ValidationError(LibcloudRestError):
    code = 1004
    name = 'Validation Error'
    message = 'An error while validating data.'

