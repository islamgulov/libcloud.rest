# -*- coding:utf-8 -*-
from werkzeug.routing import Map, Rule
import libcloud

from libcloud_rest.api.handlers import ApplicationHandler
from libcloud_rest.api.handlers import ComputeHandler
from libcloud_rest.api.versions import versions

__all__ = [
    'urls',
    ]

prefix = '/%s' % versions[libcloud.__version__]

urls = Map([Rule('/', endpoint=(ApplicationHandler, 'index'), methods=['GET']),
            Rule(prefix + '/compute/providers', endpoint=(ComputeHandler, 'providers'), methods=['GET']),
            Rule(prefix + '/compute/<string:provider>/nodes', endpoint=(ComputeHandler, 'list_nodes'),
                methods=['GET'])])

