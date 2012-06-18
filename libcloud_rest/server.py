# -*- coding:utf-8 -*-

#fix path
import os
import sys

sys.path.append(os.sep.join(
    os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-1]))

from werkzeug.serving import run_simple
import werkzeug
from gevent.monkey import patch_all
from gevent import wsgi
from libcloud_rest.application import LibcloudRestApp


def cli_start_server():
    app = LibcloudRestApp()

    if __debug__:
        run_simple('127.0.0.1', 5000, app, use_debugger=True,
                   use_reloader=True)
    else:
        patch_all()

        @werkzeug.serving.run_with_reloader
        def run_server():
            ws = wsgi.WSGIServer(('127.0.0.1', 5000), app)
            ws.serve_forever()


if __name__ == '__main__':
    cli_start_server()
