# -*- coding:utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json

from libcloud.utils.misc import get_driver
from libcloud_rest.exception import MissingArguments, UnknownArgument,\
    ProviderNotSupportedError, MissingHeadersError, UnknownHeadersError
from libcloud_rest.api.validators import validate_driver_arguments
from libcloud_rest.api.parser import ARGS_TO_XHEADERS_DICT

__all__ = [
    'get_providers_names',
    'get_driver_by_provider_name',
]


def get_providers_dict(drivers, providers):
    """
    List of all supported providers.

    @param providers: object that contain supported providers.
    @type  providers: L{libcloud.types.Provider}

    @return C{list} of C{dict} objects
    """
    result = []
    for provider_name in providers.__dict__.keys():
        if provider_name.startswith('_'):
            continue
        provider_name = provider_name.upper()
        try:
            Driver = get_driver_by_provider_name(drivers,
                                                 providers, provider_name)
            result.append({
                'id': provider_name.upper(),
                'friendly_name': getattr(Driver, 'name', ''),
                'website': getattr(Driver, 'website', ''),
            })
        except ProviderNotSupportedError:
            pass
    return result


def get_driver_by_provider_name(drivers, providers, provider_name):
    """
    Get a driver by provider name
    If the provider is unknown, will raise an exception.

    @param drivers: Dictionary containing valid providers.

    @param providers: object that contain supported providers.
    @type providers: L{libcloud.types.Provider}

    @param    provider_name:   String with a provider name (required)
    @type     provider_name:   str

    @return: L{NodeDriver} class

    """
    provider_name = provider_name.upper()
    provider = getattr(providers, provider_name, None)
    try:
        Driver = get_driver(drivers, provider)
    except AttributeError:
        raise ProviderNotSupportedError(provider=provider_name)
    return Driver


def get_driver_instance(Driver, **kwargs):
    """

    @param Driver:
    @param kwargs:
    @return:
    """
    try:
        validate_driver_arguments(Driver, kwargs)
    except MissingArguments, error:
        str_repr = ', '.join((
            ' or '.join(ARGS_TO_XHEADERS_DICT[arg] for arg in args)
            for args in error.arguments
        ))
        raise MissingHeadersError(headers=str_repr)
    except UnknownArgument, error:
        raise UnknownHeadersError(headers=str(error.arguments))
    driver = Driver(**kwargs)
    return driver


class ExtJSONEndoder(json.JSONEncoder):
    def __init__(self, obj_attrs, *args, **kwargs):
        self.obj_attrs = obj_attrs
        indent = kwargs.pop('indent', 4)
        super(ExtJSONEndoder, self).__init__(indent=indent, *args, **kwargs)

    def default(self, obj):
        for obj_attr_cls in self.obj_attrs:
            if isinstance(obj, obj_attr_cls):
                render_attrs = self.obj_attrs[obj_attr_cls]
                break
        else:
            try:
                iterable = iter(obj)
            except TypeError:
                raise KeyError('Unknown object type: %s' % (str(type(obj))))
            else:
                return list(iterable)
        return dict(
            ((a_name, getattr(obj, a_name)) for a_name in render_attrs)
        )
