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
    typename = None

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

    def get_description_dict(self):
        return {'name': self.name,
                'description': self.description,
                'type': self.typename,
                'required': self.required}


class StringField(Field):
    validator_cls = valid.StringValidator
    typename = 'string'


class LIbcloudObjectEntryBase(type):
    """
    Metaclass for all entries.
    """

    def __new__(cls, name, bases, attrs):
        super_new = super(LIbcloudObjectEntryBase, cls).__new__
        parents = [b for b in bases if isinstance(b, LIbcloudObjectEntryBase)]
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


class BasicEntry(object):
    """
    Just describe interface.
    """

    @classmethod
    def get_json_and_validate(cls, data):
        pass

    @classmethod
    def get_arguments(cls):
        pass


class LibcloudObjectEntry(object):
    __metaclass__ = LIbcloudObjectEntryBase


    @classmethod
    def get_json_and_validate(cls, data):
        try:
            json_data = json.loads(data)
        except ValueError, e:
            raise MalformedJSONError(detail=str(e))
        for field in cls._fields:
            field.validate(json_data)
        return json_data

    @classmethod
    def get_arguments(cls):
        return [field.get_description_dict() for field in cls._fields]


class SimpleEntry(BasicEntry):
    def __init__(self, name, typename, description):
        self.name = name
        self.field = simple_types_fields[typename](description, name)

    def get_json_and_validate(self, data):
        try:
            json_data = json.loads(data)
        except ValueError, e:
            raise MalformedJSONError(detail=str(e))
        self.field.validate(json_data)

    def get_arguments(self):
        return [self.field.get_description_dict()]


class NodeEntry(LibcloudObjectEntry):
    node_id = StringField('ID of the size which should be used')


simple_types_fields = {
    'C{str}': StringField,
    }

complex_entries = {
    'L{Node}': NodeEntry,
    }




def get_entry(name, typename, description=''):
    if typename in simple_types_fields:
        return SimpleEntry(name, typename, description)
    elif typename in complex_entries:
        raise NotImplementedError
