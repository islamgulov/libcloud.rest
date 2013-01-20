# -*- coding:utf-8 -*-
from werkzeug.routing import Map, Submount
import libcloud

from libcloud_rest.api.handlers import app_handler
from libcloud_rest.api.handlers.compute import compute_handler
from libcloud_rest.api.handlers.dns import dns_handler
from libcloud_rest.api.handlers.loadbalancer import lb_handler
from libcloud_rest.api.handlers.storage import storage_handler
from libcloud_rest.api.versions import versions


api_version = '/%s' % (versions[libcloud.__version__])


urls = Map([
    app_handler.get_rules(),
    Submount(api_version, [
        compute_handler.get_rules(),
        dns_handler.get_rules(),
        lb_handler.get_rules(),
        storage_handler.get_rules(),
    ])
])
