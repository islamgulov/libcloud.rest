# -*- coding:utf-8 -*-
import logging


def _init_logger():
    logger = logging.Logger('libcloud.rest', level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s : %(levelname)-8s :'
                                  ' %(message)s',
                                  '%d %b %Y %H:%M:%S')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = _init_logger()
