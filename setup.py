# -*- coding:utf-8 -*-
import os
import sys

from setuptools import setup
from setuptools import Command
from subprocess import call


class Pep8Command(Command):
    description = "run pep8 script"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import pep8
            pep8
        except ImportError:
            print ('Missing "pep8" library. You can install it using pip: '
                  'pip install pep8')
            sys.exit(1)

        cwd = os.getcwd()
        retcode = call(('pep8 %s/libcloud_rest/ %s/tests/' %
                (cwd, cwd)).split(' '))
        sys.exit(retcode)

setup(
    name='libcloud_rest',
    version='0.0.1',
    packages=[
        'libcloud_rest',
        'libcloud_rest.api',
        ],
    package_dir={'libcloud_rest': 'libcloud_rest'},
    install_requires=[
        'Werkzeug==0.8.3',
        'apache-libcloud>=0.9.1',
        'argparse==1.2.1',
        'simplejson==2.5.2',
        'wsgiref==0.1.2',
        ],
    url='https://github.com/islamgulov/libcloud.rest/',
    license='Apache License (2.0)',
    author='ilgiz',
    author_email='',
    description='REST Interface for Libcloud',
    entry_points='''
            [console_scripts]
            libcloud_rest = libcloud_rest.server:cli_start_server
            ''',
    cmdclass={
        'pep8': Pep8Command,
    },
)
