# -*- coding:utf-8 -*-
import traceback
import sys

from werkzeug.exceptions import HTTPException
from werkzeug.urls import url_decode

from libcloud_rest.api.urls import urls
from libcloud_rest.api import validators as valid
from libcloud_rest.log import logger
from libcloud_rest.errors import LibcloudRestError
from .errors import LibcloudRestError, InternalError
from libcloud_rest.constants import MAX_BODY_LENGTH
from libcloud_rest.utils import json
from libcloud_rest.api.handlers import StorageHandler
from .wrappers import Request, Response


class LibcloudRestApp(object):
    url_map = urls

    def dispatch(self, controller, action_name, request, params):
        """

        @param controller:
        @param action_name:
        @param request:
        @param params:
        @return:
        """
        request_header_validator = valid.DictValidator({
            'Content-Length': valid.IntegerValidator(max=MAX_BODY_LENGTH),
            'Content-Type': valid.ConstValidator('application/json'),
        })
        controller.request = request
        controller.params = params
        action = getattr(controller, action_name)
        if request.method == 'GET':
            data = url_decode(request.query_string, cls=dict)
            request.data = json.dumps(data)
        if request.method in ['POST', 'PUT'] and\
                not isinstance(controller, StorageHandler):
            request_header_validator(dict(request.headers))
        retval = action()
        return retval

    def dispatch_request(self, request):
        (handler_class, action) = request.url_rule
        handler = handler_class()
        return self.dispatch(handler, action, request, request.args)

    def make_response(self, *args):
        """
        Can take response or tuple of body, status, headers
        """
        rv, status, headers = args + (None, ) * (3 - len(args))
        if rv is None:
            raise ValueError('Empty response')
        if not isinstance(rv, Response):
            if isinstance(rv, basestring):
                rv = Response(rv, status, headers)
                status, headers = None, None
            else:
                raise ValueError('Response return value does not supported')
        if status is not None:
            if isinstance(status, basestring):
                rv.status = status
            else:
                rv.status_code = status
        if headers is not None:
            rv.headers.extend(headers)

        return rv

    def handle_exception(self, e, request):
        #TODO: make this handler defined function
        exc_type, exc_value, tb = sys.exc_info()
        assert exc_value is e

        if issubclass(exc_type, LibcloudRestError):
            error = e
            logger.debug('Exception on %s [%s]' % (
                request.path,
                request.method),
                exc_info=(exc_type, exc_value, tb)
            )
        else:
            error = InternalError(detail=str(e))
            logger.error('Exception on %s [%s]' % (
                request.path,
                request.method),
                exc_info=(exc_type, exc_value, tb)
            )
        return self.make_response(error.to_json(), error.http_status_code)

    def __call__(self, environ, start_response):
        request = Request(environ)
        logger.debug('%s - %s %s' %
                     (request.remote_addr, request.method, request.url))
        urls = self.url_map.bind_to_environ(environ)
        try:
            request.url_rule, request.args = urls.match()
            response = self.dispatch_request(request)
        except Exception, e:
            response = self.handle_exception(e, request)
        return response(environ, start_response)
