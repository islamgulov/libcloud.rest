# -*- coding:utf-8 -*-
from libcloud.utils.misc import get_driver

from libcloud_rest.exception import NotSupportedProviderError

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
        driver = get_driver(drivers, provider)
    except AttributeError:
        raise NotSupportedProviderError(provider=provider_name)
    return driver





