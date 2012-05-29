# -*- coding:utf-8 -*-

#fix path
import os
import sys
sys.path.append(os.sep.join(
    os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-1]))

from libcloud_rest.application import LibcloudRestApp


def cli_start_server():
    from werkzeug.serving import run_simple

    app = LibcloudRestApp()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

if __name__ == '__main__':
    cli_start_server()
