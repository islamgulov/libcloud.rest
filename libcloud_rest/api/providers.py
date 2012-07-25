# -*- coding:utf-8 -*-
import inspect
import re

from libcloud.utils.misc import get_driver

from libcloud_rest.api.parser import ARGS_TO_XHEADERS_DICT,\
    parse_args, parse_docstring, get_method_docstring
from libcloud_rest.api.validators import validate_driver_arguments
from libcloud_rest.errors import ProviderNotSupportedError,\
    MissingArguments, MissingHeadersError, UnknownArgument,\
    UnknownHeadersError, MethodParsingException, ValidationError
from libcloud_rest.api.entries import Entry
from libcloud_rest.utils import json


class DriverMethod(object):
    _type_name_pattern = r'.\{([_0-9a-zA-Z]+)\}'

    def __init__(self, driver, method_name):
        #FIXME GK
        if inspect.isclass(driver):
            self.driver_cls = driver
        else:
            self.driver_cls = driver.__class__
        self.driver = driver

        self.driver_cls = self.driver_cls
        self.method_name = method_name
        self.method = getattr(self.driver, method_name, None)
        if not inspect.ismethod(self.method):
            raise MethodParsingException('Bad method.')
        method_doc = get_method_docstring(self.driver_cls, method_name)
        if not method_doc:
            raise MethodParsingException('Empty docstring')
        argspec_arg = parse_args(self.method)
        docstring_parse_result = parse_docstring(method_doc, self.driver_cls)
        self.description = docstring_parse_result['description']
        docstring_args = docstring_parse_result['arguments']
        #check required and merge args
        self.required_entries = []
        self.optional_entries = []
        #check vargs
        self.vargs_entries = []
        for name, arg_info in argspec_arg.iteritems():
            if name in docstring_args:
                doc_arg = docstring_args[name]
                entry_kwargs = {'name': name,
                                'type_name': doc_arg['type_name'],
                                'description': doc_arg['description']}
                if not doc_arg['required'] and 'default' in arg_info:
                    entry_kwargs['default'] = arg_info['default']
                self.vargs_entries.append(Entry(**entry_kwargs))
            else:
                raise MethodParsingException(
                    '%s %s not described in docstring' % (method_name, name))
        #update kwargs
        kwargs = set(docstring_args).difference(argspec_arg)
        for arg_name in kwargs:
            arg = docstring_args[arg_name]
            entry = Entry(arg_name, arg['type_name'], arg['description'])
            if arg['required']:
                self.required_entries.append(entry)
            else:
                self.optional_entries.append(entry)
        method_return = docstring_parse_result['return']
        self.result_entry = Entry('', method_return['type_name'],
                                  method_return['description'])

    @classmethod
    def _remove_type_name_brackets(cls, type_name):
        return re.sub(cls._type_name_pattern, r'\1', type_name)

    def get_description(self):
        result_arguments = []
        for entry in self.vargs_entries:
            arguments = entry.get_arguments()
            if hasattr(entry, 'default'):
                for arg in arguments:
                    arg['required'] = False
            result_arguments.extend(arguments)
        for entry in self.required_entries:
            arguments = entry.get_arguments()
            result_arguments.extend(arguments)
        for entry in self.optional_entries:
            arguments = entry.get_arguments()
            for arg in arguments:
                arg['required'] = False
            result_arguments.extend(arguments)
        result = {'name': self.method_name,
                  'description': self.description,
                  'arguments': result_arguments,
                  'return': {
                      'type': self._remove_type_name_brackets(
                          self.result_entry.type_name),
                      'description': self.result_entry.description}
                  }
        return result

    def invoke(self, request):
        vargs = [e.from_json(request.data, self.driver)
                 for e in self.vargs_entries]
        kwargs = dict((e.name, e.from_json(request.data, self.driver))
                      for e in self.required_entries)
        for opt_arg in self.optional_entries:
            if opt_arg.contains_arguments(request.data):
                kwargs[opt_arg.name] = \
                    opt_arg.from_json(request.data, self.driver)
        result = self.method(*vargs, **kwargs)
        return self.result_entry.to_json(result)


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
