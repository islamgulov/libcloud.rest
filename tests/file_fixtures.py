# -*- coding:utf-8 -*-
from __future__ import with_statement
import functools

import os

import libcloud


FIXTURES_ROOT = {
    'compute': 'compute/fixtures',
    'storage': 'storage/fixtures',
    'loadbalancer': 'loadbalancer/fixtures',
    'dns': 'dns/fixtures',
    }

FIXTURES_PREFIX_DIR = {
    '0.10.1': 'v0_10',  # libcloud version:folder
    '0.10.0': 'v0_10'
}


class FileFixtures(object):
    def __init__(self, fixtures_type, sub_dir=''):
        script_dir = os.path.abspath(os.path.split(__file__)[0])
        self.root = os.path.join(
            script_dir,
            FIXTURES_ROOT[fixtures_type],
            FIXTURES_PREFIX_DIR[libcloud.__version__],
            sub_dir)

    def load(self, file):
        path = os.path.join(self.root, file)
        if os.path.exists(path):
            kwargs = {}
            with open(path, 'r', **kwargs) as fh:
                content = fh.read()
                return unicode(content)
        else:
            raise IOError(path)


ComputeFixtures = functools.partial(FileFixtures, 'compute')
