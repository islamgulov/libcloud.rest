# -*- coding:utf-8 -*-
from libcloud.dns.drivers.rackspace import RackspaceUSDNSDriver
from test.dns.test_rackspace import RackspaceMockHttp

from tests.patch import BaseDriverPatch


class RackspaceDNSPatch(BaseDriverPatch):
    """
    In this drivers we save RackspaceMockHttp type in preprocess
    and return back in postprocess
    """
    conn_classes = (None, RackspaceMockHttp)

    def preprocess(self, Driver):
        self._mock_type = RackspaceMockHttp.type
        RackspaceMockHttp.type = None
        Driver.connectionCls.conn_classes = self.conn_classes

    def postprocess(self, driver):
        driver.connection.poll_interval = 0.0
        # normally authentication happens lazily, but we force it here
        driver.connection._populate_hosts_and_request_paths()
        RackspaceMockHttp.type = self._mock_type

PATCHES = {
    RackspaceUSDNSDriver.__name__: RackspaceDNSPatch()
}
