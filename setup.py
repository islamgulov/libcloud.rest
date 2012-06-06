# -*- coding:utf-8 -*-
import os
import sys

from setuptools import setup
from setuptools import Command
from subprocess import call
from unittest import TextTestRunner, TestLoader
from glob import glob
from os.path import splitext, basename, join as pjoin

TEST_PATHS = ['tests', 'tests/compute', ]

SUPPORTED_VERSIONS = ['2.5', '2.6', '2.7', 'PyPy', ]

if sys.version_info <= (2, 4):
    version = '.'.join([str(x) for x in sys.version_info[:3]])
    print('Version ' + version + ' is not supported. Supported versions are ' +
          ', '.join(SUPPORTED_VERSIONS))
    sys.exit(1)


class TestCommand(Command):
    description = "run test suite"
    user_options = []

    def initialize_options(self):
        THIS_DIR = os.path.abspath(os.path.split(__file__)[0])
        sys.path.insert(0, THIS_DIR)
        for test_path in TEST_PATHS:
            sys.path.insert(0, pjoin(THIS_DIR, test_path))
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        try:
            import mock

            mock
        except ImportError:
            print('Missing "mock" library. mock is library is needed '
                  'to run the tests. You can install it using pip: '
                  'pip install mock')
            sys.exit(1)

        status = self._run_tests()
        sys.exit(status)

    def _run_tests(self):
        pre_python26 = (sys.version_info[0] == 2
                        and sys.version_info[1] < 6)
        if pre_python26:
            missing = []
            # test for dependencies
            try:
                import simplejson
                simplejson              # silence pyflakes
            except ImportError:
                missing.append("simplejson")

            try:
                import ssl
                ssl                     # silence pyflakes
            except ImportError:
                missing.append("ssl")

            if missing:
                print("Missing dependencies: " + ", ".join(missing))
                sys.exit(1)

        testfiles = []
        for test_path in TEST_PATHS:
            for t in glob(pjoin(self._dir, test_path, 'test_*.py')):
                testfiles.append('.'.join(
                    [test_path.replace('/', '.'), splitext(basename(t))[0]]))

        tests = TestLoader().loadTestsFromNames(testfiles)

        #        for test_module in DOC_TEST_MODULES:
        #            tests.addTests(doctest.DocTestSuite(test_module))

        t = TextTestRunner(verbosity=2)
        res = t.run(tests)
        return not res.wasSuccessful()


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
        'test': TestCommand,
        },
)
