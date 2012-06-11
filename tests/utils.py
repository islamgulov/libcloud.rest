# -*- coding:utf-8 -*-

__all__ = [
    'get_driver_mock_http',
]


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
        raise NotImplementedError


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
