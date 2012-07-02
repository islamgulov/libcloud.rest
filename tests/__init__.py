# -*- coding:utf-8 -*-
from os.path import dirname, join as pjoin, isfile
import shutil

from libcloud_rest import server
from libcloud import test


def setup_secrets():
    test_dir = dirname(test.__file__)
    secrets_dist_path = pjoin(test_dir, 'secrets.py-dist')
    secrets_path = pjoin(test_dir, 'secrets.py')
    if isfile(secrets_path):
        return
    shutil.copy(secrets_dist_path, secrets_path)


setup_secrets()
server.DEBUG = True
#server.setup_logger('DEBUG', None)
