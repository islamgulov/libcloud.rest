# -*- coding:utf-8 -*-
from libcloud.loadbalancer.drivers.rackspace import RackspaceLBDriver
from libcloud.test.loadbalancer.test_rackspace import RackspaceLBMockHttp


from tests.patch import BaseDriverPatch, ConnClassDriverPatch


class RackspaceLBPatch(BaseDriverPatch):
    """
    In this drivers we save RackspaceMockHttp type in preprocess
    and return back in postprocess
    """

    def pre_process(self, Driver):
        self._mock_type = RackspaceLBMockHttp.type
        RackspaceLBMockHttp.type = None
        Driver.connectionCls.conn_classes = (None,
                                             RackspaceLBMockHttp)

    def post_process(self, driver):
        driver.connection.poll_interval = 0.0
        # normally authentication happens lazily, but we force it here
        driver.connection._populate_hosts_and_request_paths()
        RackspaceLBMockHttp.type = self._mock_type

PATCHES = {
    RackspaceLBDriver.__name__: RackspaceLBPatch(),
}
