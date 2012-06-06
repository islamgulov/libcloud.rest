# -*- coding:utf-8 -*-
from libcloud_rest.exception import MissingHeaderError
from libcloud_rest.api.parser import ARGS_TO_XHEADERS_DICT

__all__ = [
    'validate_header_arguments',
    ]


def validate_header_arguments(required_arguments, arguments):
    """

    @param required_arguments:
    @param arguments:
    """
    for arg_altertives in required_arguments:
        if not any([arg in arguments for arg in arg_altertives]):
            header_names = [ARGS_TO_XHEADERS_DICT[arg]
                            for arg in arg_altertives]
            raise MissingHeaderError(header=' or '.join(header_names))
