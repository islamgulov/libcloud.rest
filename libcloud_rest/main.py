# -*- coding:utf-8 -*-
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response
from version import version
import libcloud

import simplejson as json

class BaseController(object):
    def json_response(self, obj):
        encoder = json.JSONEncoder()
        reply = encoder.iterencode(obj)
        return Response(reply, mimetype='application/json')


class ApplicationController(BaseController):
    def index(self):
        response = {
            "General API information": "http://goo.gl/Ano2O",
            "GitHub page": "https://github.com/islamgulov/libcloud.rest",
            "libcloud_version": libcloud.__version__,
            "api_version": version,
            }
        return self.json_response(response)


class ComputeController(BaseController):
    def providers(self):
        from libcloud.compute.providers import Provider
        from libcloud_rest.common import get_providers_names

        response = {
            'providers': get_providers_names(Provider),
            }
        return self.json_response(response)


class LibcloudRestApp(object):
    def __init__(self):
        prefix = '/%s' % version
        self.url_map = Map([
            Rule('/', endpoint=(ApplicationController, 'index'), methods=['GET']),
            Rule(prefix + '/compute/providers', endpoint=(ComputeController, 'providers'), methods=['GET']),
            ])

    def dispatch(self, controller, action_name, request, params):
        controller.request = request
        controller.params = params
        print action_name
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


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    app = LibcloudRestApp()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
