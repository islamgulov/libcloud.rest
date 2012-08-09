# -*- coding:utf-8 -*-
import traceback

from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
from werkzeug.exceptions import HTTPException
from werkzeug.urls import url_decode

from libcloud_rest.api.urls import urls
from libcloud_rest.api import validators as valid
from libcloud_rest.log import logger
from libcloud_rest.errors import LibcloudRestError
from libcloud_rest.constants import MAX_BODY_LENGTH
from libcloud_rest.utils import json


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
            'Content-Length': valid.IntegerValidator(max=MAX_BODY_LENGTH),
            'Content-Type': valid.ConstValidator('application/json'),
        })
        controller.request = request
        controller.params = params
        action = getattr(controller, action_name)
        try:
            if request.method == 'GET':
                data = url_decode(request.query_string, cls=dict)
                request.data = json.dumps(data)
            if request.method in ['POST', 'PUT']:
                request_header_validator(dict(request.headers))
            retval = action()
            return retval
        except LibcloudRestError, error:
            logger.debug(traceback.format_exc())
            return Response(error.to_json(), status=error.http_status_code,
                            mimetype='application/json')
        except Exception, error:
            logger.warning(traceback.format_exc())
            fake_error = LibcloudRestError(detail=str(error))  # FIXME
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
