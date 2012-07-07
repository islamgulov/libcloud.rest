# -*- coding:utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json

from libcloud_rest.api import validators as valid
from libcloud_rest.exception import MalformedJSONError, ValidationError, \
    NoSuchObjectError, MissingArguments


class Field(object):
    """
    Base class for all field types.
    """
    validator_cls = None
    typename = None

    def __init__(self, description=None, name=None, required=True):
        self.description = description
        self.name = name
        self._required = required
        self.validator = self.validator_cls(required=required, name=name)

    def _set_required(self, required):
        self._required = required

    def _get_required(self):
        return self._required

    required = property(_get_required, _set_required)

    def validate(self, json_data):
        try:
            data = json_data[self.name]
        except (KeyError, TypeError):
            if self.required:
                raise MissingArguments([self.name])
            return
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


class LibcloudObjectEntryBase(type):
    """
    Metaclass for all entries.
    """

    def __new__(mcs, name, bases, attrs):
        super_new = super(LibcloudObjectEntryBase, mcs).__new__
        parents = [b for b in bases if isinstance(b, LibcloudObjectEntryBase)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(mcs, name, bases, attrs)
            # Create the class.
        module = attrs.pop('__module__', None)
        new_class = super_new(mcs, name, bases, {'__module__': module})
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
    def _get_json(self, data):
        try:
            json_data = json.loads(data)
        except (ValueError, TypeError), e:
            raise MalformedJSONError(detail=str(e))
        if not isinstance(json_data, dict):
            raise MalformedJSONError('Bad json format')
        return json_data

    def _validate(self, json_data):
        pass

    def _get_json_and_validate(self, data):
        json_data = self._get_json(data)
        self._validate(json_data)
        return json_data

    def get_arguments(self):
        pass

    def to_json(self, obj):
        pass

    def from_json(self, obj, driver):
        pass


class LibcloudObjectEntry(BasicEntry):
    __metaclass__ = LibcloudObjectEntryBase
    render_attrs = None

    def __init__(self, name, typename, description, **kwargs):
        self.name = name
        self.typename = typename
        self.description = description
        if 'default' in kwargs:
            self.default = kwargs['default']

    @classmethod
    def to_json(cls, obj):
        try:
            data = dict(((name, getattr(obj, name))
                        for name in cls.render_attrs))
        except AttributeError, e:
            #FIXME: create new error class for this
            raise ValueError('Can not represent object as json %s' % (str(e)))
        return json.dumps(data)

    def _get_object(self, json_data, driver):
        raise NotImplementedError()

    def from_json(self, data, driver):
        missed_arguments = []
        json_data = self._get_json(data)
        try:
            self._validate(json_data)
        except MissingArguments, error:
            missed_arguments.extend(error.arguments)
        if missed_arguments:
            if [field for field in self._fields if field.name in json_data] \
                    or (not hasattr(self, 'default')):
                raise MissingArguments(arguments=missed_arguments)
            return self.default
        return self._get_object(json_data, driver)

    def _validate(self, json_data):
        for field in self._fields:
            field.validate(json_data)

    @classmethod
    def get_arguments(cls):
        return [field.get_description_dict() for field in cls._fields]


class SimpleEntry(BasicEntry):
    def __init__(self, name, typename, description, **kwargs):
        self.name = name
        if 'default' in kwargs:
            self.default = kwargs['default']
        self.field = simple_types_fields[typename](description, name)

    def _validate(self, json_data):
        self.field.validate(json_data)

    def get_arguments(self):
        return [self.field.get_description_dict()]

    def to_json(self, obj):
        try:
            data = json.dumps({self.name: obj})
            json_data = self._get_json(data)
            self._validate(json_data)
            return data
        except (MalformedJSONError, ValidationError), e:
            raise ValueError('Can not represent object as json %s' % (str(e)))

    def from_json(self, data, driver=None):
        json_data = self._get_json(data)
        try:
            self._validate(json_data)
        except MissingArguments, e:
            if hasattr(self, 'default'):
                return self.default
            raise e
        return json_data[self.name]


class NodeEntry(LibcloudObjectEntry):
    render_attrs = ['id', 'name', 'state', 'public_ips']
    node_id = StringField('ID of the size which should be used')

    def _get_object(self, json_data, driver):
        nodes_list = driver.list_nodes()
        node_id = json_data['node_id']
        for node in nodes_list:
            if node_id == node.id:
                return node
        raise NoSuchObjectError(obj_type='Node')


simple_types_fields = {
    'C{str}': StringField,
}

complex_entries = {
    'L{Node}': NodeEntry,
}


class Entry(object):
    def __new__(cls, name, typename, description='', **kwargs):
        if typename in simple_types_fields:
            entry_class = SimpleEntry
        elif typename in complex_entries:
            entry_class = complex_entries[typename]
        else:
            raise ValueError('Unknown typename')
        return entry_class(name, typename, description, **kwargs)
