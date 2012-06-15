# -*- coding:utf-8 -*-
from exceptions import BaseException
import traceback

from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
from werkzeug.exceptions import HTTPException

from libcloud_rest.api.urls import urls
from libcloud_rest.api import validators as valid
from libcloud_rest.log import logger
from libcloud_rest.exception import LibcloudRestError


class LibcloudRestApp(object):
    """
    FIXME
    """
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
            'Content-Length': valid.IntegerValidator(max=512),
            'Content-Type': valid.ConstValidator('application/json'),
        })
        controller.request = request
        controller.params = params
        action = getattr(controller, action_name)
        try:
            if request.method in ['POST', 'PUT']:
                request_header_validator(dict(request.headers))
            retval = action()
            return retval
        except LibcloudRestError, error:
            return Response(error.to_json(), status=error.http_status_code,
                mimetype='application/json')
        except BaseException, error:
            logger.debug(traceback.format_exc())
            fake_error = LibcloudRestError()  # FIXME
            return Response(
                fake_error.to_json(), status=fake_error.http_status_code,
                mimetype='application/json')  # FIXME: response error generator

    def __call__(self, environ, start_response):
        request = Request(environ)
        urls = self.url_map.bind_to_environ(environ)

        try:
            logger.debug('%s - %s %s' %
                         (request.remote_addr, request.method, request.url))
            endpoint, params = urls.match()

            (controller_class, action) = endpoint
            controller = controller_class()
            response = self.dispatch(controller, action, request, params)
        except HTTPException, e:
            response = e

        return response(environ, start_response)
