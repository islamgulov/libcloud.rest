# -*- coding:utf-8 -*-
import inspect

from libcloud_rest.errors import UnknownHeadersError

#map between request header name and libcloud's internal attribute name
XHEADERS_TO_ARGS_DICT = {
    'x-auth-user': 'key',
    'x-api-key': 'secret',
    'x-provider-path': 'path',
    'x-provider-port': 'port',
    'x-provider-host': 'host',
    'x-dummy-creds': 'creds',  # FIXME: for tests only
}

#FIXME: GK?
ARGS_TO_XHEADERS_DICT = dict(
    ([k, v] for v, k in XHEADERS_TO_ARGS_DICT.items()))

_REQUIRES_FIELD = '@requires:'


def parse_request_headers(headers):
    """
    @param headers:
    @return:
    """
    ignore_headers = ['host', 'content-type', 'content-length']
    request_headers_keys = set([key for key in set(headers.keys(lower=True))
                            if key not in ignore_headers])
    request_meta_keys = set(XHEADERS_TO_ARGS_DICT.keys())
    unknown_headers_keys = request_headers_keys.difference(request_meta_keys)
    if unknown_headers_keys:
        raise UnknownHeadersError(headers=' '.join(unknown_headers_keys))
    return dict(([XHEADERS_TO_ARGS_DICT[key], headers.get(key, None)]
        for key in request_headers_keys))


def get_method_requirements(method):
    """
    make a list of required arguments names from docstring
    @param method:
    @raise:
    @return: list of required arguments,
     every required argument described as list of alternatives
     ex. [['key'], ['secure'], ['host', 'path']]
    """
    method_docstring = inspect.getdoc(method)
    if method_docstring is None:
        raise NotImplementedError('Missing %s docstring' % _REQUIRES_FIELD)
    for docstring_line in method_docstring.splitlines():
        if docstring_line.startswith(_REQUIRES_FIELD):
            _, args = docstring_line.split(':')
            args_list = []
            for alt_arg in args.split(','):
                args_list.append([arg.strip() for arg in alt_arg.split('or')])
            return args_list
    else:
        raise NotImplementedError('Missing %s docstring' % _REQUIRES_FIELD)
