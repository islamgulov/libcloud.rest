# -*- coding:utf-8 -*-
from setuptools import setup

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
        'apache-libcloud==0.9.1',
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
)
