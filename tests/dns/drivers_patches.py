# -*- coding:utf-8 -*-
from libcloud.dns.drivers.rackspace import RackspaceUSDNSDriver
from libcloud.test.dns.test_rackspace import RackspaceMockHttp
from libcloud.dns.drivers.zerigo import ZerigoDNSDriver
from libcloud.test.dns.test_zerigo import ZerigoMockHttp
from libcloud.dns.drivers.linode import LinodeDNSDriver
from libcloud.test.dns.test_linode import LinodeMockHttp


from tests.patch import BaseDriverPatch, ConnClassDriverPatch


class RackspaceDNSPatch(BaseDriverPatch):
    """
    In this drivers we save RackspaceMockHttp type in preprocess
    and return back in postprocess
    """
    conn_classes = (None, RackspaceMockHttp)

    def pre_process(self, Driver):
        self._mock_type = RackspaceMockHttp.type
        RackspaceMockHttp.type = None
        Driver.connectionCls.conn_classes = self.conn_classes

    def post_process(self, driver):
        driver.connection.poll_interval = 0.0
        # normally authentication happens lazily, but we force it here
        driver.connection._populate_hosts_and_request_paths()
        RackspaceMockHttp.type = self._mock_type

PATCHES = {
    RackspaceUSDNSDriver.__name__: RackspaceDNSPatch(),
    ZerigoDNSDriver.__name__: ConnClassDriverPatch(None, ZerigoMockHttp),
    LinodeDNSDriver.__name__: ConnClassDriverPatch(None, LinodeMockHttp),
}
