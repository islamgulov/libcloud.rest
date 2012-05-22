# -*- coding:utf-8 -*-
from werkzeug.wrappers import Response
import libcloud_rest
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
            "api_version": libcloud_rest.__version__,
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

