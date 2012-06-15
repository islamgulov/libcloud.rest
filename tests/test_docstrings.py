# -*- coding:utf-8 -*-
import unittest2

from libcloud.compute import providers as compute_providers

from libcloud_rest.utils import get_driver_by_provider_name
from libcloud_rest.exception import ProviderNotSupportedError
from libcloud_rest.api.parser import get_method_requirements


class TestDocstring(unittest2.TestCase):
    """
    Check @required docstring in providers classes
    """
    def test_compute_requires(self):
        providers = compute_providers.Provider
        drivers = compute_providers.DRIVERS
        for provider_name in providers.__dict__.keys():
            if not provider_name.startswith('_'):
                provider_name = provider_name.upper()
                try:
                    Driver = get_driver_by_provider_name(drivers,
                                                         providers,
                                                         provider_name)
                    try:
                        get_method_requirements(Driver.__init__)
                    except NotImplementedError:
                        try:
                            get_method_requirements(Driver.__new__)
                        except NotImplementedError:
                            raise NotImplementedError(
                                '%s provider has not @requires docstrign'
                                % provider_name)
                except ProviderNotSupportedError:
                    pass
