# -*- coding:utf-8 -*-
from functools import partial
import re

from libcloud.compute import base as compute_base
from libcloud.compute.drivers import openstack as compute_openstack
from libcloud.compute.drivers import cloudstack as compute_cloudstack
from libcloud.compute.drivers import ec2
from libcloud.common import gandi as gandi_common
from libcloud.compute.drivers import opennebula as opennebula_compute
from libcloud.common import gogrid as gogrid_common
from libcloud.compute.drivers import gogrid as gogrid_compute
from libcloud.compute.drivers import opsource as opsourse_compute
from libcloud.compute.drivers import vcloud as vcloud_compute
from libcloud.dns import types as dns_types
from libcloud.dns import base as dns_base
from libcloud.loadbalancer import base as lb_base
from libcloud.loadbalancer.drivers import rackspace as lb_rackspace
from libcloud.storage import base as storage_base

from libcloud_rest.utils import json, DateTimeJsonEncoder
from libcloud_rest.api import validators as valid
from libcloud_rest.errors import MalformedJSONError, ValidationError,\
    MissingArguments, TooManyArgumentsError


class Field(object):
    """
    Base class for all field types.
    """
    validator_cls = None
    type_name = None

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
                'type': self.type_name,
                'required': self.required}


#FIXME: not unified args
class ChoicesField(Field):
    validator_cls = valid.ChoicesValidator
    type_name = 'choices'

    def __init__(self, choices, description=None, name=None, required=True):
        self.description = description
        self.name = name
        self._required = required
        self.validator = self.validator_cls(choices,
                                            required=required, name=name)


class StringField(Field):
    validator_cls = valid.StringValidator
    type_name = 'str'


class DictField(Field):
    validator_cls = partial(valid.TypeValidator, dict)
    type_name = 'dict'


class TupleField(Field):
    validator_cls = partial(valid.TypeValidator, tuple)
    type_name = 'tuple'


class BooleanField(Field):
    validator_cls = valid.BooleanValidator
    type_name = 'bool'


class IntegerField(Field):
    validator_cls = valid.IntegerValidator
    type_name = 'int'


class FloatField(Field):
    validator_cls = valid.FloatValidator
    type_name = 'float'


class NoneField(Field):
    validator_cls = valid.NoneValidator
    type_name = 'none'


class LibcloudObjectEntryBase(type):
    """
    Metaclass for all entries.
    Store all created entries type names in entries attribute.
    """

    entries_types = {}
    class_entries = {}

    @classmethod
    def get_entry(mcs, value):
        if isinstance(value, basestring):
            return mcs.entries_types.get(value, None)
        return mcs.class_entries.get(value, None)

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
        if new_class.type_name:
            type_name = new_class.type_name
        else:
            type_name = 'L{%s}' % (new_class.object_class.__name__)
        LibcloudObjectEntryBase.entries_types[type_name] = new_class
        LibcloudObjectEntryBase.class_entries[new_class.object_class] = \
            new_class
        return new_class

    def add_to_class(cls, name, value):
        if isinstance(value, Field):
            value.contribute_to_class(cls, name)
            cls._fields.append(value)
        else:
            setattr(cls, name, value)


class EntryJsonEncoder(DateTimeJsonEncoder):
    def default(self, obj):
        entry = LibcloudObjectEntryBase.get_entry(obj.__class__)
        if entry:
            return dict(((name, getattr(obj, name))
                        for name in entry.render_attrs))
        return super(EntryJsonEncoder, self).default(obj)


class BasicEntry(object):
    """
    Just describe interface.
    """

    def __init__(self, name, type_name, description, required, **kwargs):
        self.name = name
        self.type_name = type_name
        self.description = description
        self.required = required
        if 'default' in kwargs:
            if self.required:
                ValueError('Required entry can not contain default value')
            self.default = kwargs['default']

    def _get_json(self, data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        @raise: MalformedJsonError
        """
        try:
            json_data = json.loads(data)
        except (ValueError, TypeError), e:
            raise MalformedJSONError(detail=str(e))
        return json_data

    def _validate(self, json_data):
        """

        @param json_data:
        @type json_data:
        @raise: MissingArguments
                ValidationError
        """
        pass

    def _get_json_and_validate(self, data):
        json_data = self._get_json(data)
        self._validate(json_data)
        return json_data

    def get_arguments(self):
        """

        """
        pass

    def to_json(self, obj):
        """

        @param obj:
        @type obj:
        @raise: ValueError
        """
        pass

    def from_json(self, obj, driver):
        """

        @param obj:
        @type obj:
        @param driver:
        @type driver:
        @raise: MissingArguments
                ValidationError
                _get_object errors
        """
        pass

    def contains_arguments(self, json_data):
        pass


class LibcloudObjectEntry(BasicEntry):
    """
    Libcloud object entries are classes which used to render to json and
    created from json libcloud objects.
    To provide this LibcloudObjectEntry must:
        - have `render_attrs` attribute - list of object attributes
        which should be added to json representation
        - `object_class` attribute - class that described by entry
        - overload `_get_object` method - this used to create object from json
    Optionally `type_name` attribute can be provided (by default created from
        object_class name), this attribute used to describe which for which
        `@type` annotation provided entry
    """
    __metaclass__ = LibcloudObjectEntryBase
    object_class = None
    render_attrs = None
    type_name = ''

    entry_json_render = partial(json.dumps, cls=EntryJsonEncoder)

    @classmethod
    def to_json(cls, obj):
        if not isinstance(obj, cls.object_class):
            raise ValueError('Bad object type, %s is not instance of %s' %
                             (type(obj), type(cls.object_class)))
        return cls.entry_json_render(obj)

    def _get_object(self, json_data, driver):
        raise NotImplementedError('Method not implented in %s' %
                                  (str(self.__class__)))

    def contains_arguments(self, json_data):
        return any(True for f in self._fields if f.name in json_data)

    def from_json(self, data, driver):
        json_data = self._get_json(data)
        if not self.contains_arguments(json_data)\
                and hasattr(self, 'default'):
            return self.default
        self._validate(json_data)
        return self._get_object(json_data, driver)

    def _validate(self, json_data):
        missed_args = []
        try:
            for field in self._fields:
                field.validate(json_data)
        except MissingArguments, error:
            missed_args.extend(error.arguments)
        if missed_args:
            raise MissingArguments(arguments=missed_args)

    def get_arguments(self):
        fields_args = [field.get_description_dict() for field in self._fields]
        if not self.required:
            for field_arg in fields_args:
                field_arg['required'] = False
        return fields_args


class SimpleEntry(BasicEntry):
    def __init__(self, *args, **kwargs):
        super(SimpleEntry, self).__init__(*args, **kwargs)
        self.field = simple_types_fields[self.type_name](self.description,
                                                         self.name)

    def _validate(self, json_data):
        self.field.validate(json_data)

    def get_arguments(self):
        argument_dict = self.field.get_description_dict()
        argument_dict['required'] = self.required
        if hasattr(self, 'default'):
            argument_dict['default'] = self.default
        return [argument_dict]

    def to_json(self, obj):
        try:
            if not self.name:
                return json.dumps(obj)
            data = json.dumps({self.name: obj})
            json_data = self._get_json(data)
            self._validate(json_data)
            return data
        except (MalformedJSONError, ValidationError), e:
            raise ValueError('Can not represent object as json %s' % (str(e)))

    def contains_arguments(self, json_data):
        return self.field.name in json_data

    def from_json(self, data, driver=None):
        json_data = self._get_json(data)
        if not self.contains_arguments(json_data)\
                and hasattr(self, 'default'):
            return self.default
        self._validate(json_data)
        return json_data[self.name]


class NodeEntry(LibcloudObjectEntry):
    object_class = compute_base.Node
    render_attrs = ['id', 'name', 'state', 'public_ips']
    node_id = StringField('ID of the node which should be used')

    def _get_object(self, json_data, driver=None):
        node_id = json_data['node_id']
        node = self.object_class(node_id, None, None, None, None, driver)
        return node


class NodeAuthSSHKeyEntry(LibcloudObjectEntry):
    object_class = compute_base.NodeAuthSSHKey
    render_attrs = ['pubkey']
    node_pubkey = StringField('An SSH key to be installed for'
                              ' authentication to a node.')

    def _get_object(self, json_data, driver):
        return compute_base.NodeAuthSSHKey(json_data['node_pubkey'])


class NodeAuthPasswordEntry(LibcloudObjectEntry):
    object_class = compute_base.NodeAuthPassword
    render_attrs = ['password']
    node_password = StringField('A password to be used for'
                                ' authentication to a node.')

    def _get_object(self, json_data, driver):
        return compute_base.NodeAuthPassword(json_data['node_password'])


class StorageVolumeFakeEntry(LibcloudObjectEntry):
    object_class = compute_base.StorageVolume
    volume_id = StringField('ID of the storage volume which should be used')


class NodeImageEntry(LibcloudObjectEntry):
    object_class = compute_base.NodeImage
    render_attrs = ['id', 'name']
    image_id = StringField('ID of the node image which should be used')

    def _get_object(self, json_data, driver=None):
        image_id = json_data['image_id']
        image = compute_base.NodeImage(image_id, None, driver)
        return image


class NodeSizeEntry(LibcloudObjectEntry):
    object_class = compute_base.NodeSize
    render_attrs = ('id', 'name', 'ram', 'bandwidth', 'price',)
    size_id = StringField('ID of the node size which should be used')

    def _get_object(self, json_data, driver=None):
        size_id = json_data['size_id']
        size = compute_base.NodeSize(size_id, None, None, None, None,
                                     None, driver)
        return size


class NodeLocationEntry(LibcloudObjectEntry):
    object_class = compute_base.NodeLocation
    render_attrs = ('id', 'name', 'country',)
    location_id = StringField('ID of the node location which should be used')

    def _get_object(self, json_data, driver=None):
        location_id = json_data['location_id']
        location = compute_base.NodeLocation(location_id, None, None, None)
        return location


class OpenStack_1_0_SharedIpGroupEntry(LibcloudObjectEntry):
    object_class = compute_openstack.OpenStack_1_0_SharedIpGroup
    render_attrs = ['id', 'name', 'server']
    shared_ip_group_id = StringField('ID of the shared ip '
                                     'group which should be used')


class CloudStackDiskOfferingEntry(LibcloudObjectEntry):
    object_class = compute_cloudstack.CloudStackDiskOffering
    render_attrs = ('id', 'name', 'size', 'customizable',)
    disk_offering_id = StringField('ID of a disk offering within CloudStack.')

    def _get_object(self, json_data, driver=None):
        disk_offering_id = json_data['disk_offering_id']
        return compute_cloudstack.CloudStackDiskOffering(
            disk_offering_id, None, None, None)


class CloudStackAddressEntry(LibcloudObjectEntry):
    object_class = compute_cloudstack.CloudStackAddress
    render_attrs = ('node', 'id', 'address',)
    cloudstack_address_ip = StringField('IP of address which should be used')
    cloudstack_address_id = StringField('ID of address which should be used')

    def _get_object(self, json_data, driver=None):
        cloudstack_address_ip = json_data['cloudstack_address_ip']
        cloudstack_address_id = json_data['cloudstack_address_id']
        return compute_cloudstack.CloudStackAddress(
            None, cloudstack_address_id, cloudstack_address_ip)


class CloudStackForwardingRuleEntry(LibcloudObjectEntry):
    object_class = compute_cloudstack.CloudStackForwardingRule
    render_attrs = ('node', 'id', 'address', 'protocol',
                    'start_port', 'end_port')

    cloudstack_forwarding_rule_id = StringField('ID of forwarding rule '
                                                'which should be used')

    def _get_object(self, json_data, driver=None):
        rule_id = json_data['cloudstack_forwarding_rule_id']
        return compute_cloudstack.CloudStackForwardingRule(
            None, rule_id, None, None, None)


class CloudStackNodeEntry(NodeEntry):
    object_class = compute_cloudstack.CloudStackNode


class ExEC2AvailabilityZoneEntry(LibcloudObjectEntry):
    object_class = ec2.ExEC2AvailabilityZone
    render_attrs = ('name', 'zone_state', 'region_name',)
    availability_zone_name = StringField('Name of availability zone '
                                         'which should be used')

    def _get_object(self, json_data, driver=None):
        zone_name = json_data['availability_zone_name']
        return ec2.ExEC2AvailabilityZone(
            zone_name, None, None)


class GandiDiskEntry(LibcloudObjectEntry):
    object_class = gandi_common.Disk
    type_name = 'L{GandiDisk}'
    render_attrs = ('id', 'state', 'name', 'size', 'extra',)
    gandi_disk_id = StringField('ID of Gandi disk which should be used')

    def _get_object(self, json_data, driver):
        disk_id = json_data['gandi_disk_id']
        return gandi_common.Disk(disk_id, None, None, driver, None)


class GandiNetworkInterfaceEntry(LibcloudObjectEntry):
    object_class = gandi_common.NetworkInterface
    type_name = 'L{GandiNetworkInterface}'
    render_attrs = ('id', 'mac', 'state', 'node')
    gandi_network_iface_id = StringField('ID of Gandi  network interface '
                                         'which should be used')

    def _get_object(self, json_data, driver):
        iface_id = json_data['gandi_network_iface_id']
        return gandi_common.NetworkInterface(iface_id, None, None, driver)


class GoGridIpAddressEntry(LibcloudObjectEntry):
    object_class = gogrid_common.GoGridIpAddress
    render_attrs = ('id', 'ip', 'public', 'state', 'subnet')
    gogrid_address_id = StringField('ID of address which should be used')

    def _get_object(self, json_data, driver):
        address_id = json_data['gogrid_address_id']
        return gogrid_common.GoGridIpAddress(address_id,
                                             None, None, None, None)


class GoGridNodeEntry(NodeEntry):
    object_class = gogrid_compute.GoGridNode


class OpenNebulaNetworkEntry(LibcloudObjectEntry):
    object_class = opennebula_compute.OpenNebulaNetwork
    render_attrs = ('id', 'name', 'address', 'size', 'extra')
    opennebula_network_id = StringField('ID of network which should be used')
    opennebula_network_address = StringField(
        'Address of network which should be used', required=False)

    def _get_object(self, json_data, driver):
        network_id = json_data['opennebula_network_id']
        network_address = json_data.get('opennebula_network_address', None)
        return opennebula_compute.OpenNebulaNetwork(
            network_id, None, network_address, None, driver)


class OpenNebulaNodeSizeEntry(NodeSizeEntry):
    object_class = opennebula_compute.OpenNebulaNodeSize
    render_attrs = ('id', 'name', 'ram', 'bandwidth', 'price',)
    size_id = StringField('ID of the node size which should be used')

    def _get_object(self, json_data, driver=None):
        size_id = json_data['size_id']
        return opennebula_compute.OpenNebulaNodeSize(
            size_id, None, None, None, None, None, driver)


class OpsourceNetworkEntry(LibcloudObjectEntry):
    object_class = opsourse_compute.OpsourceNetwork
    render_attrs = ('id', 'name', 'description', 'location', 'privateNet',
                    'multicast', 'status')
    opsource_network_id = StringField('ID of network which should be used')

    def _get_object(self, json_data, driver):
        network_id = json_data['opsource_network_id']
        return opsourse_compute.OpsourceNetwork(
            network_id, None, None, None, None, None, None)


class VCloudVdcEntry(LibcloudObjectEntry):
    object_class = vcloud_compute.Vdc
    type_name = 'L{VCloudVDC}'
    render_attrs = ('id', 'name')
    vcloud_vdc_id = StringField('ID of vDC which should be used')

    def _get_object(self, json_data, driver):
        vdc_id = json_data['vcloud_vdc_id']
        return vcloud_compute.Vdc(vdc_id, None, driver)


class ZoneEntry(LibcloudObjectEntry):
    object_class = dns_base.Zone
    render_attrs = ('id', 'domain', 'type', 'ttl', 'extra')
    zone_id = StringField('ID of the zone which should be used')

    def _get_object(self, json_data, driver):
        zone_id = json_data['zone_id']
        return driver.get_zone(zone_id)


class RecordTypeEntry(LibcloudObjectEntry):
    object_class = dns_types.RecordType
    _type_ids = list(v for k, v in dns_types.RecordType.__dict__.items()
                     if not k.startswith('_'))
    record_type = ChoicesField(_type_ids,
                               'Type of record which should be used')

    def _get_object(self, json_data, driver):
        return json_data['record_type']


class RecordEntry(LibcloudObjectEntry):
    object_class = dns_base.Record
    render_attrs = ('id', 'name', 'type', 'data', 'zone', 'extra')
    zone_id = StringField('ID of the zone which should be used')
    record_id = StringField('ID of the record which should be used')

    def _get_object(self, json_data, driver):
        zone_id = json_data['zone_id']
        record_id = json_data['record_id']
        return driver.get_record(zone_id, record_id)


class LoadBalancerEntry(LibcloudObjectEntry):
    object_class = lb_base.LoadBalancer
    render_attrs = ('id', 'name', 'state', 'ip', 'port', 'extra')
    loadbalancer_id = StringField(
        'ID of the load balancer which should be used')

    def _get_object(self, json_data, driver):
        id = json_data['loadbalancer_id']
        return lb_base.LoadBalancer(id, None, None, None, None, None)


class MemberEntry(LibcloudObjectEntry):
    object_class = lb_base.Member
    render_attrs = ('id', 'ip', 'port', 'extra')
    member_id = StringField('ID of the member which should be used')
    member_ip = StringField('IP of the member which should be used',
                            required=False)
    member_port = IntegerField('Port of the member which should be used',
                               required=False)
    member_extra = DictField('Extra member arguments which should be used',
                             required=False)

    def _get_object(self, json_data, driver):
        id = json_data['member_id']
        ip = json_data.get('member_ip', None)
        port = json_data.get('member_port', None)
        extra = json_data.get('member_extra', {})
        return lb_base.Member(id, ip, port, extra)


class AlgorithmEntry(LibcloudObjectEntry):
    object_class = lb_base.Algorithm
    _type_ids = list(v for k, v in lb_base.Algorithm.__dict__.items()
                     if not k.startswith('_'))
    algorithm = ChoicesField(_type_ids,
                             'ID of algorithm which should be used')

    def _get_object(self, json_data, driver):
        algorithm_id = json_data['algorithm']
        return algorithm_id


class RackspaceAccessRuleEntry(LibcloudObjectEntry):
    object_class = lb_rackspace.RackspaceAccessRule
    render_attrs = ('id', 'rule_type', 'address')
    _rule_types_ids = list(
        v for k, v in
        lb_rackspace.RackspaceAccessRuleType.__dict__.items()
        if not k.startswith('_'))
    rule_id = StringField(
        'ID of the Rackspace access rule which should be used', required=False)
    rule_type = ChoicesField(_rule_types_ids, 'RackspaceAccessRuleType')
    rule_address = StringField(
        'IP address or cidr (can be IPv4 or IPv6) of '
        'the Rackspace access rule which should be used')

    def _get_object(self, json_data, driver):
        rule_id = json_data.get('rule_id', None)
        rule_type = json_data['rule_type']
        rule_address = json_data['rule_address']
        return lb_rackspace.RackspaceAccessRule(rule_id, rule_type,
                                                rule_address)


class RackspaceAccessRuleTypeEntry(LibcloudObjectEntry):
    object_class = lb_rackspace.RackspaceAccessRuleType
    _rule_types_ids = list(
        v for k, v in
        lb_rackspace.RackspaceAccessRuleType.__dict__.items()
        if not k.startswith('_'))
    rule_type = ChoicesField(_rule_types_ids, 'RackspaceAccessRuleType')

    def _get_object(self, json_data, driver):
        return json_data['rule_type']


class RackspaceConnectionThrottle(LibcloudObjectEntry):
    object_class = lb_rackspace.RackspaceConnectionThrottle
    render_attrs = ('min_connections', 'max_connections',
                    'max_connection_rate', 'rate_interval_seconds')
    min_connections = IntegerField(
        'Connection throttle minimum number of connections per IP '
        'address before applying throttling.')
    max_connections = IntegerField(
        'Connection throttle  Maximum number of of connections per IP  '
        'address. (Must be between 0 and 100000, 0 allows an unlimited number'
        ' of connections.)')
    max_connection_rate = IntegerField(
        'Connection throttle maximum number of connections allowed from a'
        ' single IP address within the given rate_interval_seconds.  (Must be '
        'between 0 and 100000, 0 allows an unlimited number of connections.)')
    rate_interval_seconds = IntegerField(
        'Connection throttle interval at which the max_connection_rate is '
        'enforced. (Must be between 1 and 3600.)')

    def _get_object(self, json_data, driver):
        min_connections = json_data['ct_min_connections']
        max_connections = json_data['ct_max_connections']
        max_connection_rate = json_data['ct_max_connection_rate']
        rate_interval_seconds = json_data['ct_rate_interval_seconds']
        return lb_rackspace.RackspaceConnectionThrottle(min_connections,
                                                        max_connections,
                                                        max_connection_rate,
                                                        rate_interval_seconds)


class RackspaceHealthMonitorEntry(LibcloudObjectEntry):
    object_class = lb_rackspace.RackspaceHealthMonitor
    render_attrs = ('type', 'delay', 'timeout', 'attempts_before_deactivation')
    health_monitor_type = StringField(
        'type of load balancer.  currently CONNECT (connection monitoring), '
        'HTTP, HTTPS (connection and HTTP monitoring) are supported)')
    health_monitor_delay = IntegerField(
        'minimum seconds to wait before executing the health monitor. '
        '(Must be between 1 and 3600)')
    health_monitor_timeout = IntegerField(
        'maximum seconds to wait when establishing a connection before'
        ' timing out.  (Must be between 1 and 3600)')
    health_monitor_attempts_before_deactivation = IntegerField(
        'Number of monitor failures before removing a node from rotation. '
        '(Must be between 1 and 10)')

    def _get_object(self, json_data, driver):
        type = json_data['health_monitor_type']
        delay = json_data['health_monitor_delay']
        timeout = json_data['health_monitor_timeout']
        attempts_before_deactivation =\
            json_data['health_monitor_attempts_before_deactivation']
        return lb_rackspace.RackspaceHealthMonitor(
            type, delay, timeout, attempts_before_deactivation)


class ContainerEntry(LibcloudObjectEntry):
    object_class = storage_base.Container
    render_attrs = ('name', 'extra',)
    container_name = StringField('Name of container which should be used')
    container_extra = DictField('Extra of container which should be used',
                                required=False)

    def _get_object(self, json_data, driver):
        name = json_data['container_name']
        extra = json_data.get('container_extra', {})
        return storage_base.Container(name, extra, driver)


class ObjectEntry(LibcloudObjectEntry):
    object_class = storage_base.Object
    render_attrs = ('name', 'size', 'hash', 'extra', 'meta_data', 'container')
    container_name = StringField('Name of container which should be used')
    object_name = StringField('Name of object which should be used')

    def _get_object(self, json_data, driver):
        container_name = json_data['container_name']
        object_name = json_data['container_name']
        return driver.get_container(container_name, object_name)


simple_types_fields = {
    'C{str}': StringField,
    'C{dict}': DictField,
    'C{bool}': BooleanField,
    'C{int}': IntegerField,
    'C{float}': FloatField,
    'C{None}': NoneField,
    'C{tuple}': TupleField,
    'L{Deployment}': StringField,  # FIXME
    'L{UUID}': StringField,  # FIXME
}


class OneOfEntry(BasicEntry):
    def __init__(self, *args, **kwargs):
        super(OneOfEntry, self).__init__(*args, **kwargs)
        self.entries = [Entry(self.name, tn, self.description)
                        for tn in self.type_name.split(' or ')]

    def _validate(self, json_data):
        missed_arguments = []
        for entry in self.entries:
            try:
                entry._validate(json_data)
                break
            except (MissingArguments, ), e:
                missed_arguments.extend(e.arguments)
        else:
            raise MissingArguments(arguments=missed_arguments)

    def get_arguments(self):
        arguments = []
        for entry in self.entries:
            args = entry.get_arguments()
            if not self.required:
                for arg in args:
                    arg['required'] = False
            arguments.extend(args)
        return arguments

    def to_json(self, obj):
        for entry in self.entries:
            try:
                json_data = entry.to_json(obj)
                return json_data
            except (ValueError, ), e:
                continue
        else:
            raise ValueError('Can not represent object as json')

    def from_json(self, data, driver):
        missed_arguments = []
        validation_errors = []
        contain_arguments = []
        results = []
        json_data = self._get_json(data)
        for entry in self.entries:
            try:
                contain_arguments.append(entry.contains_arguments(json_data))
                results.append(entry.from_json(data, driver))
            except MissingArguments, e:
                missed_arguments.extend(e.arguments)
            except ValidationError, e:
                validation_errors.append(e)
        if len(results) == 1:
            return results[0]
        elif validation_errors:
            error_message = ' || '.join([e.message for e in validation_errors])
            raise ValidationError(error_message)
        elif not results and not any(contain_arguments)\
                and hasattr(self, 'default'):
            return self.default
        elif missed_arguments:
            missed_arguments = ' or '.join(str(a) for a in missed_arguments)
            raise MissingArguments(arguments=missed_arguments)
        raise TooManyArgumentsError


class ListEntry(BasicEntry):
    """
    #TODO: implement container entry
    """

    def __init__(self, *args, **kwargs):
        super(ListEntry, self).__init__(*args, **kwargs)
        container_type, object_type = self.type_name.split(' of ', 1)
        self.container_type = container_type.strip()
        self.object_type = object_type.strip()
        self.description = self.description
        self.object_entry = Entry('', object_type, '')

    def _validate(self, json_data):
        raise NotImplementedError

    def get_arguments(self):
        #FIXME:
        entry_arg = self.object_entry.get_arguments()
        entry_arg_json = str(entry_arg)
        result = {'name': self.name,
                  'description': self.description,
                  'type': 'list of %s' % (entry_arg_json),
                  'required': self.required}
        if hasattr(self, 'default'):
            result['default'] = str(self.default)
        return [result]

    def to_json(self, obj_list):
        data = [json.loads(self.object_entry.to_json(obj)) for obj in obj_list]
        return  json.dumps(data)

    def from_json(self, data, driver):
        json_data = self._get_json(data)
        if not self.name in json_data:
            if hasattr(self, 'default'):
                return self.default
            raise MissingArguments(arguments=[self.name])
        data_list = json_data[self.name]
        return [self.object_entry.from_json(json.dumps(data), driver)
                for data in data_list]


class Entry(object):
    _container_regex = re.compile('(.\{[_0-9a-zA-Z]+\} of .\{[_0-9a-zA-Z]+\})')

    def __new__(cls, name, type_name, description='', required=True, **kwargs):
        if not ' or ' in type_name:
            if type_name in simple_types_fields:
                entry_class = SimpleEntry
            elif LibcloudObjectEntryBase.get_entry(type_name):
                entry_class = LibcloudObjectEntryBase.get_entry(type_name)
            elif re.match(cls._container_regex, type_name):
                entry_class = ListEntry
            else:
                raise ValueError('Unknown type name %s' % (type_name))
            return entry_class(
                name, type_name, description, required, **kwargs)
        return OneOfEntry(name, type_name, description, required, **kwargs)
