# -*- coding:utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json


class MissingArguments(Exception):

    def __init__(self, arguments):
        self.arguments = arguments

    def __str__(self):
        return "Missing arguments: %s" % str(self.arguments)


class UnknownArgument(Exception):
    def __init__(self, arguments):
        self.arguments = arguments

    def __str__(self):
        return "Unknown arguments: %s" % str(self.arguments)


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


class MissingHeadersError(LibcloudRestError):
    code = 1003
    name = 'MissingHeaders'
    message = 'Your request was missing a required headers: %(headers)s.'
    http_status_code = 400


class UnknownHeadersError(LibcloudRestError):
    code = 1004
    name = 'UnknownHeaders'
    message = 'Your request is containing a unknown headers: %(headers)s.'
    http_status_code = 400


class LibcloudError(LibcloudRestError):
    code = 1005
    name = "InternalLibcloudError"
    message = "%(error)s"
    http_status_code = 500


class ValidationError(LibcloudRestError):
    def __init__(self, message):
        self.message = message

    code = 1006
    name = 'ValidationError'
    http_status_code = 400


class MalformedJSONError(LibcloudRestError):
    code = 1007
    name = 'MalformedJSON'
    http_status_code = 400
    message = 'The JSON you provided is not well-formed.'
