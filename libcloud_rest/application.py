# -*- coding:utf-8 -*-
from exceptions import BaseException
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
from werkzeug.exceptions import HTTPException

import libcloud_rest
from controllers import ApplicationController
from controllers import ComputeController
from libcloud_rest.exception import LibcloudRestError


class LibcloudRestApp(object):
    """
    FIXME
    """

    def __init__(self):
        prefix = '/%s' % libcloud_rest.__version__
        self.url_map = Map([
            Rule('/', endpoint=(ApplicationController, 'index'), methods=['GET']),
            Rule(prefix + '/compute/providers', endpoint=(ComputeController, 'providers'), methods=['GET']),
            Rule(prefix + '/compute/<string:provider>/nodes', endpoint=(ComputeController, 'list_nodes'),
                methods=['GET'])
        ])

    def dispatch(self, controller, action_name, request, params):
        """

        @param controller:
        @param action_name:
        @param request:
        @param params:
        @return:
        """
        controller.request = request
        controller.params = params
        action = getattr(controller, action_name)
        try:
            retval = action()
            return retval
        except LibcloudRestError, error:
            error_json = error.to_json()
            return Response(error_json, status=error.http_code, mimetype='application/json')
        except BaseException, error:
            print error
            fake_error = LibcloudRestError() #FIXME
            return Response(fake_error.to_json(), status=fake_error.http_code, mimetype='application/json')

    def __call__(self, environ, start_response):
        request = Request(environ)
        urls = self.url_map.bind_to_environ(environ)

        try:
            endpoint, params = urls.match()

            (controller_class, action) = endpoint
            controller = controller_class()

            response = self.dispatch(controller, action, request, params)
        except HTTPException, e:
            response = e

        return response(environ, start_response)

