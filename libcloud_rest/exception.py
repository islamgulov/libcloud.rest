# -*- coding:utf-8 -*-
import simplejson as json

class LibcloudRestError(Exception):
    """
    Base class for other Libcloud REST exceptions.
    To use this class inherit from it and define attributes.
    """

    http_code = 500
    error_code = 'Unknown.'
    error_message = "An unknown exception occurred.s "

    def __init__(self, **kwargs):
        try:
            self.error_message = self.error_message % kwargs
        except Exception:
            # kwargs doesn't match a variable in the message
            pass
        super(LibcloudRestError, self).__init__()

    def to_json(self):
        """

        @return:
        """
        data = {'error':
                        {
                        'error_code': self.error_code,
                        'error_message': self.error_message,
                        }
        }
        return json.dumps(data)


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ("<" + self.__class__.__name__ + " in "
                + repr(self.http_code)
                + " "
                + self.error_code
                + " "
                + self.error_message
                + ">")


class NotSupportedProviderError(LibcloudRestError):
    http_code = 400
    error_code = "NotSupportedProvider"
    error_message = "Provider %(provider)s does not supported."


class InternalError(LibcloudRestError):
    http_code = 500
    error_code = "InternalError"
    error_message = "We encountered an internal error."