# -*- coding:utf-8 -*-
import sys
from os.path import exists, join as pjoin

LIBCLOUD_DIR = '/home/ilgiz/dev/libcloud'


def _import_libcloud_test():
    if not exists(pjoin(LIBCLOUD_DIR, 'test')):
        print "Missing libcloud directory"
        print "Maybe you forgot to change it in: tests/__init__.py"
        sys.exit(1)
    sys.path.insert(0, LIBCLOUD_DIR)
    import test
    test
    sys.path.pop(0)

_import_libcloud_test()
