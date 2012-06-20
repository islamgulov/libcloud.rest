# -*- coding:utf-8 -*-
import httplib

try:
    import simplejson as json
except ImportError:
    import json

from libcloud.dns import types

class MissingArguments(Exception):

    def __init__(self, arguments):
        self.arguments = arguments

    def __str__(self):
        return "Missing arguments: %s" % (str(self.arguments))


class UnknownArgument(Exception):
    def __init__(self, arguments):
        self.arguments = arguments

    def __str__(self):
        return "Unknown arguments: %s" % (str(self.arguments))


class LibcloudRestError(Exception):
    """
    Base class for other Libcloud REST exceptions.
    To use this class inherit from it and define attributes.
    """

    code = 1000
    name = 'UnknownError'
    message = 'An unknown error occurred.'
    detail = ''
    http_status_code = httplib.INTERNAL_SERVER_ERROR

    def __init__(self, **kwargs):
        self.message = self.message % kwargs
        self.detail = kwargs.pop('detail', '')
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
                        'detail': self.detail,
                        }
        }
        return json.dumps(data)

    def __str__(self):
        return '%d (%s) - %s "%s"' % \
            (self.code, self.name, self.message, self.detail)


class ProviderNotSupportedError(LibcloudRestError):
    code = 1001
    name = 'ProviderNotSupported'
    message = 'Provider %(provider)s does not supported.'
    http_status_code = httplib.BAD_REQUEST


class InternalError(LibcloudRestError):
    code = 1002
    name = 'InternalError'
    message = 'We encountered an internal error.'
    http_status_code = httplib.INTERNAL_SERVER_ERROR


class MissingHeadersError(LibcloudRestError):
    code = 1003
    name = 'MissingHeaders'
    message = 'Your request was missing a required headers: %(headers)s.'
    http_status_code = httplib.BAD_REQUEST


class UnknownHeadersError(LibcloudRestError):
    code = 1004
    name = 'UnknownHeaders'
    message = 'Your request is containing a unknown headers: %(headers)s.'
    http_status_code = httplib.BAD_REQUEST


class LibcloudError(LibcloudRestError):
    code = 1005
    name = 'InternalLibcloudError'
    message = 'We encountered an internal error in libcloud.'
    http_status_code = httplib.INTERNAL_SERVER_ERROR


class ValidationError(LibcloudRestError):
    def __init__(self, message):
        self.message = message

    code = 1006
    name = 'ValidationError'
    http_status_code = httplib.BAD_REQUEST


class MalformedJSONError(LibcloudRestError):
    code = 1007
    name = 'MalformedJSON'
    http_status_code = httplib.BAD_REQUEST
    message = 'The JSON you provided is not well-formed.'

class NoSuchZoneError(LibcloudRestError):
    code = 1008
    name = 'NoSuchZone'
    http_status_code = httplib.NOT_FOUND
    message = 'The specified zone does not exist'

class ZoneAlreadyExistsError(LibcloudError):
    code = 1009
    name = 'ZoneAlreadyExists'
    http_status_code = httplib.CONFLICT
    message = 'The requested zone already exists.'

class NoSuchRecordError(LibcloudRestError):
    code = 1009
    name = 'NoSuchRecord'
    http_status_code = httplib.NOT_FOUND
    message = 'The specified record does not exist'

class RecordAlreadyExistsError(LibcloudError):
    code = 1010
    name = 'RecordAlreadyExists'
    http_status_code = httplib.CONFLICT
    message = 'The requested record already exists.'

INTERNAL_LIBCLOUD_ERRORS_MAP = {
    types.ZoneAlreadyExistsError: ZoneAlreadyExistsError,
    types.ZoneDoesNotExistError: NoSuchZoneError,
    types.RecordAlreadyExistsError: RecordAlreadyExistsError,
    types.RecordDoesNotExistError: NoSuchRecordError,
    }
