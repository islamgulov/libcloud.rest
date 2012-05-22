# -*- coding:utf-8 -*-
from libcloud_rest.application import LibcloudRestApp


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    app = LibcloudRestApp()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)


