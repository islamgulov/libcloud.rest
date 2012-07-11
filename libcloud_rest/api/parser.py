# -*- coding:utf-8 -*-
import inspect
from collections import defaultdict
from itertools import chain, takewhile
import re
import sys

from libcloud_rest.utils import LastUpdatedOrderedDict
from libcloud_rest.constants import REQUIRES_FIELD

#map between request header name and libcloud's internal attribute name
XHEADERS_TO_ARGS_DICT = {
    'x-auth-user': 'key',
    'x-api-key': 'secret',
    'x-provider-path': 'path',
    'x-provider-port': 'port',
    'x-provider-host': 'host',
    'x-dummy-creds': 'creds',  # FIXME: for tests only
    'x-provider-key': 'key',
    'x-provider-uri': 'uri',
    'x-provider-api-version': 'api_version'
}

#FIXME: GK?
ARGS_TO_XHEADERS_DICT = dict(
    ([k, v] for v, k in XHEADERS_TO_ARGS_DICT.items()))


def parse_request_headers(headers):
    """
    @param headers:
    @return:
    """
    request_headers_keys = set(headers.keys(lower=True))
    request_meta_keys = set(XHEADERS_TO_ARGS_DICT.keys())
    data_headers_keys = request_headers_keys.intersection(request_meta_keys)
    return dict(([XHEADERS_TO_ARGS_DICT[key], headers.get(key, None)]
                for key in data_headers_keys))


def get_method_requirements(method):
    """
    make a list of required arguments names from docstring
    @param method:
    @raise:
    @return: list of required arguments,
     every required argument described as list of alternatives
     ex. [['key'], ['secure'], ['host', 'path']]
    """
    method_docstring = inspect.getdoc(method)
    if method_docstring is None:
        raise NotImplementedError('Missing %s docstring' % (REQUIRES_FIELD))
    for docstring_line in method_docstring.splitlines():
        if docstring_line.startswith(REQUIRES_FIELD):
            _, args = docstring_line.split(':')
            args_list = []
            for alt_arg in args.split(','):
                args_list.append([arg.strip() for arg in alt_arg.split('or')])
            return args_list
    else:
        raise NotImplementedError('Missing %s docstring' % (REQUIRES_FIELD))


def get_method_docstring(cls, method_name):
    """
    return method  docstring
    if method docstring is empty we get docstring from parent
    @param method:
    @type method:
    @return:
    @rtype:
    """
    method = getattr(cls, method_name, None)
    if method is None:
        return
    docstrign = inspect.getdoc(method)
    if docstrign is None:
        for base in cls.__bases__:
            docstrign = get_method_docstring(base, method_name)
            if docstrign:
                return docstrign
        else:
            return None
    return docstrign


def _parse_types_names(type_str):
    """
    parse types names from field string and return list of types names
    for example:
        C{str} or L{Node} -> ['C{str}', 'L{Node}]
        C{list} of C{str} -> ['C{list} of C{str}']
    @param type_str:
    @type type_str:
    @return:
    @rtype:
    """
    return [ftype.strip() for ftype in type_str.split(' or ')]


def _parse_docstring_field(field_lines):
    """

    @param field_string:
    @type field_string:
    @return: return pair:
        argument name, dict of updates for argument info
    @rtype: C{dict}
    """
    if field_lines.startswith('@type'):
        field_data = field_lines.split(None, 2)
        arg_name = field_data[1].strip(':')
        arg_type = _parse_types_names(field_data[2])
        return  arg_name, {'type_names': arg_type}
    if field_lines.startswith('@keyword') or field_lines.startswith('@param'):
        field_data = field_lines.split(None, 2)
        arg_name = field_data[1].strip(':')
        arg_description = field_data[2].strip()
        return arg_name, {'description': arg_description,
                          'required': '(required)' in arg_description}


def _find_parent_cls(cls, cls_name):
    if cls.__name__ == cls_name:
        return cls
    for base_cls in cls.__bases__:
        res = _find_parent_cls(base_cls, cls_name)
        if res is not None:
            return res
    return None


def _parse_inherit(cls, inherits):
    regex = r".\{(?P<cls_name>[_0-9a-zA-Z]+).(?P<method_name>[_0-9a-zA-Z]+)\}"
    m = re.match(regex, inherits.strip())
    cls_name = m.group('cls_name')
    method_name = m.group('method_name')
    parent_cls = _find_parent_cls(cls, cls_name)
    docstring = get_method_docstring(parent_cls, method_name)
    return parse_docstring(docstring, parent_cls)


def parse_docstring(docstring, cls=None):
    """
    NB. by default arguments marked as optional
    @param docstring:
    @type docstring:
    @return: return tuple
        description - method description
        arguments - dict of dicts arg_name: {desctiption, type_names, required}
        return - list of return types
    @rtype: C{dict}
    """
    def_arg_dict = lambda: {'description': None,
                            'type_names': None,
                            'required': False,
                            }
    arguments_dict = defaultdict(def_arg_dict)
    return_value_types = []
    docstring_list = docstring.splitlines()
    #parse description
    description_list = []
    for lineno, orig_line in enumerate(docstring_list):
        docstring_line = orig_line.strip()
        if docstring_line.startswith('@'):
            break
        description_list.append(docstring_line)
    description = '\n'.join(description_list)
    field_indent = lambda l: sum(1 for _ in takewhile(lambda c: c != ':', l))
    space_indent = lambda l: sum(1 for _ in takewhile(lambda c: c == ' ', l))
    #parse fields
    cached_field = None
    cached_filed_indent = 0
    for docstring_line in chain(docstring_list, '@'):
        orig_docstring_line = docstring_line
        docstring_line = docstring_line.strip()
        if docstring_line.startswith('@'):
            if cached_field is None or cached_field.startswith('@return'):
                cached_field = ''
            #parse inherits
            elif cached_field.startswith('@inherits'):
                if not cls:
                    raise ValueError
                inherit_str = cached_field.split(':', 1)[1]
                result = _parse_inherit(cls, inherit_str)
                if not description and result[0]:
                    description = result[0]
                for arg_name, update_dict in result[1].items():
                    arguments_dict[arg_name].update(update_dict)
                return_value_types = result[2]
            #parse return value
            elif cached_field.startswith('@rtype'):
                types_str = cached_field.split(':', 1)[1]
                return_value_types = _parse_types_names(types_str)
            #parse arguments
            else:
                arg_name, update_dict = _parse_docstring_field(cached_field)
                arguments_dict[arg_name].update(update_dict)
        if cached_field is not None:
            if docstring_line.startswith('@'):
                cached_filed_indent = field_indent(orig_docstring_line)
                cached_field = docstring_line + '\n'
            else:
                if space_indent(orig_docstring_line) >= cached_filed_indent:
                    cached_field += docstring_line + '\n'
                else:
                    cached_filed_indent = sys.maxint
    #check fields
    for argument, info in arguments_dict.iteritems():
        if info['type_names'] is None:
            raise ValueError('Can not get  @type for argument %s' %
                             (argument))
        if info['description'] is None:
            raise ValueError('Can not get description for argument %s' %
                             (argument))
    if not return_value_types:
        raise ValueError('Can not get return types for argument')
    return description, arguments_dict, return_value_types


def parse_args(method):
    args, varargs, varkw, argspec_defaults = inspect.getargspec(method)
    if inspect.ismethod(method):
        args.pop(0)
    defaults = LastUpdatedOrderedDict()
    if argspec_defaults is not None:
        defaults = dict(zip(reversed(args), reversed(argspec_defaults)))
    args_dict = LastUpdatedOrderedDict()
    for arg in args:
        if arg in defaults:
            args_dict[arg] = {
                'required': False,
                'default': defaults[arg]
            }
        else:
            args_dict[arg] = {'required': True, }
    return  args_dict
