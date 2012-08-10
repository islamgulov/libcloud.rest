# -*- coding:utf-8 -*-
from libcloud.storage.drivers.cloudfiles import CloudFilesUSStorageDriver
from libcloud.test.storage.test_cloudfiles import CloudFilesMockHttp,\
    CloudFilesMockRawResponse


from tests.patch import BaseDriverPatch, ConnClassDriverPatch


class CloudFilesPatch(BaseDriverPatch):
    """
    In this drivers we save RackspaceMockHttp type in preprocess
    and return back in postprocess
    """

    def pre_process(self, Driver):
        self._mock_type = CloudFilesMockHttp.type
        self._raw_type = CloudFilesMockRawResponse.type
        CloudFilesMockHttp.type = None
        CloudFilesMockRawResponse.type = None
        Driver.connectionCls.conn_classes = (None,
                                             CloudFilesMockHttp)
        Driver.connectionCls.rawResponseCls = CloudFilesMockRawResponse

    def post_process(self, driver):
        # normally authentication happens lazily, but we force it here
        driver.connection._populate_hosts_and_request_paths()
        CloudFilesMockHttp.type = self._mock_type
        CloudFilesMockRawResponse.type = self._raw_type

PATCHES = {
    CloudFilesUSStorageDriver.__name__: CloudFilesPatch(),
}
