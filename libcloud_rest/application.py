# -*- coding:utf-8 -*-
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request
from werkzeug.exceptions import HTTPException

import libcloud_rest
from controllers import ApplicationController
from controllers import ComputeController


class LibcloudRestApp(object):
    def __init__(self):
        prefix = '/%s' % libcloud_rest.__version__
        self.url_map = Map([
            Rule('/', endpoint=(ApplicationController, 'index'), methods=['GET']),
            Rule(prefix + '/compute/providers', endpoint=(ComputeController, 'providers'), methods=['GET']),
            ])

    def dispatch(self, controller, action_name, request, params):
        controller.request = request
        controller.params = params
        action = getattr(controller, action_name)
        retval = action()

        return retval

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

