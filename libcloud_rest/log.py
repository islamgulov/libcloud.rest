# -*- coding:utf-8 -*-
import logging

logger = logging


def get_logger(handler, level):
    logger = logging.Logger('libcloud.rest', level=level)
    formatter = logging.Formatter('%(asctime)s : %(levelname)-8s :'
                                  ' %(message)s',
                                  '%d %b %Y %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

