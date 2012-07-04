# -*- coding:utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json

from libcloud_rest.api import validators as valid
from libcloud_rest.exception import MalformedJSONError


class Field(object):
    """
    Base class for all field types.
    """
    validator_cls = None

    def __init__(self, description=None, name=None, required=True):
        self.description = description
        self.name = name
        self.required = required
        self.validator = self.validator_cls(required=required, name=name)

    def validate(self, json_data):
        data = json_data.get(self.name, None)
        if self.required or data:
            self.validator(data)

    def contribute_to_class(self, cls, name):
        self.model = cls
        self.name = name
        self.validator.name = name


class StringField(Field):
    validator_cls = valid.StringValidator


class EntryBase(type):
    """
    Metaclass for all entries.
    """

    def __new__(cls, name, bases, attrs):
        super_new = super(EntryBase, cls).__new__
        parents = [b for b in bases if isinstance(b, EntryBase)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(cls, name, bases, attrs)
        # Create the class.
        module = attrs.pop('__module__', None)
        new_class = super_new(cls, name, bases, {'__module__': module})
        new_class.add_to_class('_fields', [])

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        return new_class

    def add_to_class(cls, name, value):
        if isinstance(value, Field):
            value.contribute_to_class(cls, name)
            cls._fields.append(value)
        else:
            setattr(cls, name, value)


class Entry(object):
    __metaclass__ = EntryBase

    @classmethod
    def validate(cls, data):
        try:
            json_data = json.loads(data)
        except ValueError, e:
            raise MalformedJSONError(detail=str(e))
        for field in cls._fields:
            field.validate(json_data)


class NodeEntry(Entry):
    node_id = StringField('ID of the size which should be used')


simple_types_fields = {
    'C{str}': StringField,
}

complex_entries = {
    'L{Node}': NodeEntry,
}


def create_simple_entry(name, typename, description):
    entry_name = name.capitalize() + 'Entry'
    entry_field = simple_types_fields[typename](description)
    return type(entry_name, (Entry,), {name: entry_field})


def get_entry(name, typename, description=''):
    if typename in simple_types_fields:
        return create_simple_entry(name, typename, description)
    elif typename in complex_entries:
        raise NotImplementedError
