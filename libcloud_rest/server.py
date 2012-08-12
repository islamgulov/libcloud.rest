# -*- coding:utf-8 -*-
import os
import sys
import logging
from optparse import OptionParser

sys.path.append(os.sep.join(
    os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-1]))

import libcloud_rest.log
from libcloud_rest.log import get_logger
from libcloud_rest.constants import VALID_LOG_LEVELS

DEBUG = False


def start_server(host, port, logger, debug):
    from werkzeug.serving import run_simple
    from libcloud_rest.application import LibcloudRestApp
    import werkzeug

    app = LibcloudRestApp()

    if debug:
        logger.info('Debug HTTP server listening on %s:%s' % (host, port))
        run_simple(host, port, app,
                   use_debugger=True, use_reloader=True)
    else:
        from gevent.monkey import patch_all
        from gevent import pywsgi as wsgi

        patch_all()
        logger.info('HTTP server listening on %s:%s' % (host, port))

        @werkzeug.serving.run_with_reloader
        def run_server():
            class debug_logger(object):
                @staticmethod
                def write(*args, **kwargs):
                    logger.debug(*args, **kwargs)

            ws = wsgi.WSGIServer((host, port), app, log=debug_logger)
            ws.serve_forever()


def setup_logger(log_level, log_file):
    # Mute default werkzeug logger
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)

    # Setup main logger
    if not log_file:
        handler = logging.StreamHandler()
    else:
        handler = logging.FileHandler(filename=log_file)

    new_logger = get_logger(handler=handler, level=log_level)
    libcloud_rest.log.logger = new_logger
    return new_logger


def main():
    usage = 'usage: %prog'
    parser = OptionParser(usage=usage)
    parser.add_option('--host', dest='host', default='localhost',
                      help='Host to bind to', metavar='HOST')
    parser.add_option('--port', dest='port', default=5000,
                      help='Port to listen on', metavar='PORT')
    parser.add_option('--log-level', dest='log_level', default='info',
                      help='Log level', metavar='LEVEL')
    parser.add_option('--log-file', dest='log_file', default=None,
                      help='Log file path. If not provided'
                           ' logs will go to stdout',
                      metavar='PATH')
    parser.add_option('--debug', dest='debug', default=False,
                      action='store_true', help='Enable debug mode')

    (options, args) = parser.parse_args()

    log_level = options.log_level.upper()
    log_file = options.log_file

    if log_level not in VALID_LOG_LEVELS:
        valid_levels = [value.lower() for value in VALID_LOG_LEVELS]
        raise ValueError('Invalid log level: %s. Valid log levels are: %s' %
                         (options.log_level, ', ' .join(valid_levels)))

    if options.debug:
        log_level = 'DEBUG'
        global DEBUG
        DEBUG = True

    level = getattr(logging, log_level, logging.INFO)

    logger = setup_logger(log_level=level, log_file=log_file)
    start_server(host=options.host, port=int(options.port),
                 logger=logger, debug=options.debug)


if __name__ == '__main__':
    main()
