# -*- coding:utf-8 -*-
import inspect

from libcloud.utils.misc import get_driver

from libcloud_rest.api.parser import ARGS_TO_XHEADERS_DICT,\
    parse_args, parse_docstring, get_method_docstring
from libcloud_rest.api.validators import validate_driver_arguments
from libcloud_rest.errors import ProviderNotSupportedError,\
    MissingArguments, MissingHeadersError, UnknownArgument,\
    UnknownHeadersError, MethodParsingException
from libcloud_rest.api.entries import Entry
from libcloud_rest.utils import json

REQUEST_METHOD_TYPES = {
    'GET': ('get', 'list', 'describe', ),
    'POST': ('create', ),
    'PUT': ('edit', 'set', 'change', ),
    'DELETE': ('destroy', 'delete', ),

}


class DriverMethod(object):
    def __init__(self, driver_cls, method_name):
        self.driver_cls = driver_cls
        self.method_name = method_name
        method = getattr(driver_cls, method_name, None)
        if not inspect.ismethod(method):
            raise MethodParsingException('Bad method.')
        self._init_request_method()
        method_doc = get_method_docstring(driver_cls, method_name)
        if not method_doc:
            raise MethodParsingException('Empty docstring')
        argspec_arg = parse_args(method)
        description, docstring_args, returns =\
            parse_docstring(method_doc, driver_cls)
        self.description = description
        #check required and merge args
        self.required_entries = []
        self.optional_entries = []
        #check vargs
        for name, arg_info in argspec_arg.iteritems():
            if name in docstring_args:
                doc_arg = docstring_args[name]
                entry_kwargs = {'name': name,
                                'type_names': doc_arg['type_names'],
                                'description': doc_arg['description']}
                if not doc_arg['required'] and 'default' in arg_info:
                    entry_kwargs['default'] = arg_info['default']
                    self.optional_entries.append(Entry(**entry_kwargs))
                else:
                    self.required_entries.append(Entry(**entry_kwargs))
            else:
                raise MethodParsingException(
                    '%s %s not described in docstring' % (method_name, name))
                #update kwargs
        kwargs = set(docstring_args).difference(argspec_arg)
        for arg_name in kwargs:
            arg = docstring_args[arg_name]
            entry = Entry(arg_name, arg['type_names'], arg['description'])
            if arg['required']:
                self.required_entries.append(entry)
            else:
                self.optional_entries.append(entry)
        self.result_entry = Entry('', returns, '')

    def _init_request_method(self):
        for method_type, supported_kw in REQUEST_METHOD_TYPES.items():
            for kw in supported_kw:
                if kw in self.method_name:
                    self.request_method = method_type
                    return method_type
        raise MethodParsingException('unknown http request method')

    def get_description(self):
        result_arguments = []
        for entry in self.required_entries:
            arguments = entry.get_arguments()
            for arg in arguments:
                arg['required'] = True
            result_arguments.extend(arguments)
        for entry in self.optional_entries:
            arguments = entry.get_arguments()
            for arg in arguments:
                if isinstance(arg, basestring):
                    print arg
                arg['required'] = False
            result_arguments.extend(arguments)
        result = {'name': self.method_name,
                  'description': self.description,
                  'arguments': result_arguments}
        return result

    def invoke(self, data):
        raise NotImplementedError


def get_providers_info(drivers, providers):
    """
    List of all supported providers.

    @param providers: object that contain supported providers.
    @type  providers: L{libcloud.types.Provider}

    @return C{list} of C{dict} objects
    """
    result = []
    for provider, Driver in get_providers_dict(drivers, providers).items():
        result.append({
            'id': provider,
            'friendly_name': getattr(Driver, 'name', ''),
            'website': getattr(Driver, 'website', ''),
        })
    return result


def get_providers_dict(drivers, providers):
    result = {}
    for provider_name in providers.__dict__.keys():
        if provider_name.startswith('_'):
            continue

        provider_name = provider_name.upper()
        try:
            Driver = get_driver_by_provider_name(drivers,
                                                 providers,
                                                 provider_name)
            result[provider_name] = Driver
        except ProviderNotSupportedError:
            continue
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
