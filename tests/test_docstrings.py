# -*- coding:utf-8 -*-
import unittest2

from libcloud.compute import providers as compute_providers
from libcloud.dns import providers as dns_providers

from libcloud_rest.utils import get_driver_by_provider_name
from libcloud_rest.exception import ProviderNotSupportedError
from libcloud_rest.api.parser import get_method_requirements


class TestDocstring(unittest2.TestCase):
    """
    Check @required docstring in providers classes
    """

    @staticmethod
    def _get_drivers(providers, drivers):
        result = []
        for provider_name in providers.__dict__.keys():
            if provider_name.startswith('_'):
                continue

            provider_name = provider_name.upper()
            try:
                Driver = get_driver_by_provider_name(drivers,
                                                     providers,
                                                     provider_name)
                result.append(Driver)
            except ProviderNotSupportedError:
                continue
        return result

    @classmethod
    def _check_requires(cls, providers, drivers):
        Drivers = cls._get_drivers(providers, drivers)
        for Driver in Drivers:
            for method in [Driver.__init__, Driver.__new__]:
                try:
                    get_method_requirements(method)
                    break
                except NotImplementedError:
                    pass
            else:
                raise NotImplementedError(
                    '%s driver has not @requires docstrign'
                    % (str(Driver)))

    @classmethod
    def _check_website(cls, providers, drivers):
        Drivers = cls._get_drivers(providers, drivers)
        without_website_attr = []
        for Driver in Drivers:
            website = getattr(Driver, 'website', None)
            if website is None:
                without_website_attr.append(Driver)
        if without_website_attr:
            raise NotImplementedError(
                '%s drivers have not website attribute'
                % (str(without_website_attr)))

    def test_compute_requires(self):
        providers = compute_providers.Provider
        drivers = compute_providers.DRIVERS
        self._check_requires(providers, drivers)

    def test_dns_requires(self):
        providers = dns_providers.Provider
        drivers = dns_providers.DRIVERS
        self._check_requires(providers, drivers)

    def test_compute_provider_website(self):
        providers = compute_providers.Provider
        drivers = compute_providers.DRIVERS
        self._check_website(providers, drivers)

    def test_dns_provider_website(self):
        providers = dns_providers.Provider
        drivers = dns_providers.DRIVERS
        self._check_website(providers, drivers)
