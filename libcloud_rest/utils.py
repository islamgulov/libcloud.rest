# -*- coding:utf-8 -*-
import inspect

from libcloud.utils.misc import get_driver
from libcloud_rest.exception import ProviderNotSupportedError

__all__ = [
    "get_providers_names",
    "get_driver_by_provider_name",
    ]


def get_providers_names(providers):
    """
    List of all supported providers.

    @param providers: object that contain supported providers.
    @type  providers: L{libcloud.types.Provider}

    @return C{list} of C{str} objects
    """
    return [prov for prov in providers.__dict__.keys() if not prov.startswith('_')]


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
    try:
        provider = getattr(providers, provider_name)
        Driver = get_driver(drivers, provider)
    except AttributeError:
        raise ProviderNotSupportedError(provider=provider_name)
    return Driver


def get_driver_instance(Driver, username, password):
    """

    @param Driver:
    @param username:
    @param password:
    @return:
    """
    if inspect.isbuiltin(Driver.__new__):
        arg_spec = inspect.getargspec(Driver.__init__)
    else:
        arg_spec = inspect.getargspec(Driver.__new__)
    if 'secure' in arg_spec.args:
        driver = Driver(username, password)
    else:
        driver = Driver(username)
    return driver
