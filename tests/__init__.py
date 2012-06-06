# -*- coding:utf-8 -*-
import sys

LIBCLOUD_DIR = '/home/ilgiz/dev/libcloud'


def _import_libcloud_test():
    sys.path.insert(0, LIBCLOUD_DIR)
    import test
    test
    sys.path.pop(0)

_import_libcloud_test()
