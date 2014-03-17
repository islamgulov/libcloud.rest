# -*- coding:utf-8 -*-
from libcloud.compute.drivers.dummy import DummyNodeDriver
from libcloud.common.base import ConnectionKey
from libcloud.compute.drivers.gogrid import GoGridNodeDriver
from libcloud.test.compute.test_gogrid import GoGridMockHttp
from libcloud.compute.drivers.cloudstack import CloudStackNodeDriver
from libcloud.test.compute.test_cloudstack import CloudStackMockHttp
from libcloud.compute.drivers.rackspace import RackspaceNodeDriver
from libcloud.test.compute.test_openstack import OpenStackMockHttp

from tests.patch import ConnClassDriverPatch, BaseDriverPatch


class RackspaceComputePatch(BaseDriverPatch):
    def pre_process(self, Driver):
        # monkeypatch get_endpoint because the base openstack driver doesn't
        #actually work with old devstack but this class/tests are still
        # used by the rackspace driver
        def get_endpoint(*args, **kwargs):
            return "https://servers.api.rackspacecloud.com/v1.0/slug"
        self._mock_type = OpenStackMockHttp.type
        OpenStackMockHttp.type = None
        Driver.connectionCls.get_endpoint = get_endpoint
        Driver.connectionCls.conn_classes = (OpenStackMockHttp,
                                             OpenStackMockHttp)
        Driver.connectionCls.auth_url = "https://auth.api.example.com/v1.1/"
        self._mock_type = OpenStackMockHttp.type

    def post_process(self, driver):
        # normally authentication happens lazily, but we force it here
        driver.connection._populate_hosts_and_request_paths()
        OpenStackMockHttp.type = self._mock_type


PATCHES = {
    DummyNodeDriver.__name__: ConnClassDriverPatch(ConnectionKey,
                                                   ConnectionKey),
    GoGridNodeDriver.__name__: ConnClassDriverPatch(None,
                                                    GoGridMockHttp),
    CloudStackNodeDriver.__name__: ConnClassDriverPatch(None,
                                                        CloudStackMockHttp),
    RackspaceNodeDriver.__name__: RackspaceComputePatch(),
}
