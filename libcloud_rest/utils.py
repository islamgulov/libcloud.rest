# -*- coding:utf-8 -*-
import inspect

from libcloud.utils.misc import get_driver
from libcloud_rest.errors import ProviderNotSupportedError
from libcloud_rest.api.parser import get_method_requirements
from libcloud_rest.api.validators import validate_header_arguments

__all__ = [
    'get_providers_names',
    'get_driver_by_provider_name',
    ]


def get_providers_names(providers):
    """
    List of all supported providers.

    @param providers: object that contain supported providers.
    @type  providers: L{libcloud.types.Provider}

    @return C{list} of C{str} objects
    """
    return [pr for pr in providers.__dict__.keys() if not pr.startswith('_')]


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
    if provider is None:
        raise ProviderNotSupportedError(provider=provider_name)
    Driver = get_driver(drivers, provider)
    return Driver


def get_driver_instance(Driver, **kwargs):
    """

    @param Driver:
    @param kwargs:
    @return:
    """
    try:
        required_args = get_method_requirements(Driver.__init__)
    except NotImplementedError:
        required_args = get_method_requirements(Driver.__new__)
    #FIXME:validate for extra args
    validate_header_arguments(required_args, kwargs)
    driver = Driver(**kwargs)
    return driver
