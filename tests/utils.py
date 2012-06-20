# -*- coding:utf-8 -*-
import copy


def patch_driver(Driver):
    Driver_copy = copy.deepcopy(Driver)
    Driver_copy.connectionCls.conn_classes = get_driver_mock_http(
        Driver.__name__)
    return Driver_copy


def get_driver_mock_http(driver_name):
    if driver_name in DRIVERS_MOCK_HTTP:
        http_conn, https_conn = DRIVERS_MOCK_HTTP[driver_name]
        result = []
        for conn in DRIVERS_MOCK_HTTP[driver_name]:
            if conn is None:
                result.append(None)
            else:
                mod_name, conn_name = conn
                _mod = __import__(mod_name, globals(), locals(), [conn_name])
                result.append(getattr(_mod, conn_name))
        return result
    else:
        raise NotImplementedError('Unknown driver %s' % (driver_name))


COMPUTE_MOCK_HTTP = {
    'DummyNodeDriver':
        [('libcloud.common.base', 'ConnectionKey'),
            ('libcloud.common.base', 'ConnectionKey')],
    'GoGridNodeDriver':
        [None, ('test.compute.test_gogrid', 'GoGridMockHttp')],
    'CloudStackNodeDriver':
        [None, ('test.compute.test_cloudstack', 'CloudStackMockHttp')],
}

DRIVERS_MOCK_HTTP = COMPUTE_MOCK_HTTP

DNS_MOCK_HTTP = {
    'RackspaceUSDNSDriver':
        [None, ('test.dns.test_rackspace', 'RackspaceMockHttp')],
}

DRIVERS_MOCK_HTTP.update(DNS_MOCK_HTTP)
