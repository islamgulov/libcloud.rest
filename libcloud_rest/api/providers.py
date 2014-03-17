# -*- coding:utf-8 -*-
import inspect
import re

from libcloud.utils.misc import get_driver

from libcloud_rest.api.parser import ARGS_TO_XHEADERS_DICT,\
    parse_args, parse_docstring, get_method_docstring
from libcloud_rest.errors import ProviderNotSupportedError,\
    MissingArguments, MissingHeadersError, MethodParsingException,\
    NoSuchOperationError
from libcloud_rest.api.entries import Entry
from libcloud_rest.utils import json


class DriverMethod(object):
    _type_name_pattern = r'.\{([_0-9a-zA-Z]+)\}'

    def __init__(self, driver_obj, method_name):
        if inspect.isclass(driver_obj):
            self.driver_cls = driver_obj
        else:
            self.driver_cls = driver_obj.__class__
        self.driver_obj = driver_obj
        self.method_name = method_name
        self.method = getattr(self.driver_obj, method_name, None)
        if not inspect.ismethod(self.method):
            raise NoSuchOperationError()
        method_doc = get_method_docstring(self.driver_cls, method_name)
        if not method_doc:
            raise MethodParsingException('Empty docstring')
        argspec_arg = parse_args(self.method)
        docstring_parse_result = parse_docstring(method_doc, self.driver_cls)
        self.description = docstring_parse_result['description']
        docstring_args = docstring_parse_result['arguments']
        #check vargs
        self.vargs_entries = []
        for name, arg_info in argspec_arg.iteritems():
            if name in docstring_args:
                docstring_arg = docstring_args[name]
                entry_kwargs = {
                    'name': name,
                    'description': docstring_arg['description'],
                    'type_name': docstring_arg['type_name'],
                    'required': (docstring_arg['required'] or
                                 arg_info['required']),
                }
                if not entry_kwargs['required'] and 'default' in arg_info:
                    entry_kwargs['default'] = arg_info['default']
                self.vargs_entries.append(Entry(**entry_kwargs))
            else:
                raise MethodParsingException(
                    '%s %s not described in docstring' % (method_name, name))
            #update kwargs
        kwargs = set(docstring_args).difference(argspec_arg)
        self.kwargs_entries = [Entry(arg_name, **docstring_args[arg_name])
                               for arg_name in kwargs]
        method_return = docstring_parse_result['return']
        self.result_entry = Entry('', method_return['type_name'],
                                  method_return['description'], True)

    @classmethod
    def _remove_type_name_brackets(cls, type_name):
        return re.sub(cls._type_name_pattern, r'\1', type_name)

    def get_description(self):
        result_arguments = []
        for entry in self.vargs_entries:
            result_arguments.extend(entry.get_arguments())
        for entry in self.kwargs_entries:
            result_arguments.extend(entry.get_arguments())
        result = {'name': self.method_name,
                  'description': self.description,
                  'arguments': result_arguments,
                  'return': {
                      'type': self._remove_type_name_brackets(
                          self.result_entry.type_name),
                      'description': self.result_entry.description}
                  }
        return result

    def invoke_result_to_json(self, value):
        return self.result_entry.to_json(value)

    def invoke(self, data):
        vargs = [e.from_json(data, self.driver_obj)
                 for e in self.vargs_entries]
        kwargs = {}
        for kw_entry in self.kwargs_entries:
            try:
                kwargs[kw_entry.name] = kw_entry.from_json(data,
                                                           self.driver_obj)
            except MissingArguments:
                if kw_entry.required:
                    raise
        if self.method_name == '__init__':
            return self.driver_cls(*vargs, **kwargs)
        return self.method(*vargs, **kwargs)


def get_providers_info(providers):
    """
    List of all supported providers.

    @param providers: object that contain supported providers.
    @type  providers: L{libcloud.types.Provider}

    @return C{list} of C{dict} objects
    """
    result = []
    for provider, Driver in get_providers_dict(providers.DRIVERS,
                                               providers.Provider).items():
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


def get_driver_instance(Driver, kwargs):
    """

    @param Driver:
    @param kwargs:
    @return:
    """
    try:
        json_data = json.dumps(kwargs)
        driver_method = DriverMethod(Driver, '__init__')
        return driver_method.invoke(json_data)
    except MissingArguments, error:
        str_repr = ', '.join([ARGS_TO_XHEADERS_DICT.get(arg, arg)
                              for arg in error.arguments])
        raise MissingHeadersError(headers=str_repr)
