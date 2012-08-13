# -*- coding:utf-8 -*-
import unittest2
from inspect import getmembers, ismethod

from libcloud.compute import providers as compute_providers
from libcloud.dns import providers as dns_providers
from libcloud.loadbalancer import providers as lb_providers
from libcloud.storage import providers as storage_providers
from libcloud.test import secrets

from libcloud_rest.api.providers import get_driver_by_provider_name
from libcloud_rest.errors import ProviderNotSupportedError
from libcloud_rest.api.providers import DriverMethod


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
    def _check_docstrings(cls, providers, drivers):
        Drivers = cls._get_drivers(providers, drivers)
        for Driver in Drivers:
            methods = [mn for mn, _ in getmembers(Driver, ismethod) if
                       not mn.startswith('_')]
            methods.append('__init__')
            for method_name in methods:
                try:
                    DriverMethod(Driver, method_name)
                except Exception, e:
                    print str(e), Driver.name, method_name

    @classmethod
    def _check_website(cls, providers, drivers):
        Drivers = cls._get_drivers(providers, drivers)
        without_website_attr = []
        for Driver in Drivers:
            website = getattr(Driver, 'website', None)
            name = getattr(Driver, 'name', None)
            if website is None or name is None:
                without_website_attr.append(Driver.__name__)
        if without_website_attr:
            raise NotImplementedError(
                '%s drivers have not website or name attribute'
                % (str(without_website_attr)))

    def test_compute_docstrings(self):
        providers = compute_providers.Provider
        drivers = compute_providers.DRIVERS
        self._check_docstrings(providers, drivers)

    def test_dns_docstrings(self):
        providers = dns_providers.Provider
        drivers = dns_providers.DRIVERS
        self._check_docstrings(providers, drivers)

    def test_loadbalancer_docstrings(self):
        providers = lb_providers.Provider
        drivers = lb_providers.DRIVERS
        self._check_docstrings(providers, drivers)

    def test_storage_docstrings(self):
        providers = storage_providers.Provider
        drivers = storage_providers.DRIVERS
        self._check_docstrings(providers, drivers)

    def test_compute_provider_website(self):
        providers = compute_providers.Provider
        drivers = compute_providers.DRIVERS
        self._check_website(providers, drivers)

    def test_dns_provider_website(self):
        providers = dns_providers.Provider
        drivers = dns_providers.DRIVERS
        self._check_website(providers, drivers)

    def test_loadbalacner_provider_website(self):
        providers = lb_providers.Provider
        drivers = lb_providers.DRIVERS
        self._check_website(providers, drivers)

    def test_storage_provider_website(self):
        providers = storage_providers.Provider
        drivers = storage_providers.DRIVERS
        self._check_website(providers, drivers)
