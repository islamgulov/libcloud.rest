# -*- coding:utf-8 -*-
from libcloud.compute.drivers.dummy import DummyNodeDriver
from libcloud.common.base import ConnectionKey
from libcloud.compute.drivers.gogrid import GoGridNodeDriver
from test.compute.test_gogrid import GoGridMockHttp
from libcloud.compute.drivers.cloudstack import CloudStackNodeDriver
from test.compute.test_cloudstack import CloudStackMockHttp
from tests.patch import ConnClassDriverPatch

PATCHES = {
    DummyNodeDriver.__name__: ConnClassDriverPatch(ConnectionKey,
                                                   ConnectionKey),
    GoGridNodeDriver.__name__: ConnClassDriverPatch(None,
                                                    GoGridMockHttp),
    CloudStackNodeDriver.__name__: ConnClassDriverPatch(None,
                                                        CloudStackMockHttp),
    }
