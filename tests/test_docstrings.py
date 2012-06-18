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
            if provider_name.startswith('_'):
                continue

            provider_name = provider_name.upper()
            try:
                Driver = get_driver_by_provider_name(drivers,
                                                     providers,
                                                     provider_name)
            except ProviderNotSupportedError:
                continue

            for method in [Driver.__init__, Driver.__new__]:
                try:
                    get_method_requirements(method)
                    break
                except NotImplementedError:
                    pass
            else:
                raise NotImplementedError(
                    '%s provider has not @requires docstrign'
                    % provider_name)
