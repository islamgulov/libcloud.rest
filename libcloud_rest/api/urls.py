# -*- coding:utf-8 -*-
from werkzeug.routing import Map, Rule, Submount, RuleTemplate
import libcloud

from libcloud_rest.api.handlers import ApplicationHandler
from libcloud_rest.api.handlers import ComputeHandler
from libcloud_rest.api.handlers import DNSHandler
from libcloud_rest.api.versions import versions

api_version = '/%s' % (versions[libcloud.__version__])

providers_list_rule = Rule(
    '/providers', endpoint=(ComputeHandler, 'providers'),
    methods=['GET'])

list_objects_rule_template = RuleTemplate([Rule(
    '/<string:provider>/$objects', defaults={'method_name': 'list_$objects'},
    endpoint=(ComputeHandler, 'invoke_method'), methods=['GET'])])

compute_urls = Submount('/compute/', [
    providers_list_rule,
    Rule('/providers/<string:provider_name>',
         endpoint=(ComputeHandler, 'provider_info'),
         methods=['GET']),
    list_objects_rule_template(objects='nodes'),
    list_objects_rule_template(objects='images'),
    list_objects_rule_template(objects='sizes'),
    list_objects_rule_template(objects='locations'),
    Rule('/<string:provider>/nodes', endpoint=(ComputeHandler, 'create_node'),
         methods=['POST']),
    Rule('/<string:provider>/nodes/<string:node_id>/reboot',
         endpoint=(ComputeHandler, 'reboot_node'),
         methods=['POST']),
    Rule('/<string:provider>/nodes/<string:node_id>',
         endpoint=(ComputeHandler, 'destroy_node'),
         methods=['DELETE']),
    Rule('/<string:provider>/<string:method_name>',
         endpoint=(ComputeHandler, 'invoke_method'),
         methods=['POST']),
])

storage_urls = Submount('/storage/', [
    providers_list_rule,
])

loadbalancer_urls = Submount('/loadbalancer/', [
    providers_list_rule,
])

dns_urls = Submount('/dns/', [
    providers_list_rule,
    Rule('/<string:provider>/zones', endpoint=(DNSHandler, 'list_zones'),
         methods=['GET']),
    Rule('/<string:provider>/zones/<string:zone_id>/records',
         endpoint=(DNSHandler, 'list_records'),
         methods=['GET']),
    Rule('/<string:provider>/zones', endpoint=(DNSHandler, 'create_zone'),
         methods=['POST']),
    Rule('/<string:provider>/zones/<string:zone_id>',
         endpoint=(DNSHandler, 'update_zone'),
         methods=['PUT']),
    Rule('/<string:provider>/zones/<string:zone_id>',
         endpoint=(DNSHandler, 'delete_zone'),
         methods=['DELETE']),
    Rule('/<string:provider>/zones/<string:zone_id>'
         '/records/<string:record_id>',
         endpoint=(DNSHandler, 'get_record'),
         methods=['GET']),
    Rule('/<string:provider>/zones/<string:zone_id>/records',
         endpoint=(DNSHandler, 'create_record'),
         methods=['POST']),
    Rule('/<string:provider>/zones/<string:zone_id>/'
         'records/<string:record_id>',
         endpoint=(DNSHandler, 'update_record'),
         methods=['PUT']),
    Rule('/<string:provider>/zones/<string:zone_id>/'
         'records/<string:record_id>',
         endpoint=(DNSHandler, 'delete_record'),
         methods=['DELETE']),
])

urls = Map([
    Rule('/', endpoint=(ApplicationHandler, 'index'), methods=['GET']),
    Submount(api_version, [
        compute_urls,
        storage_urls,
        loadbalancer_urls,
        dns_urls,
    ])
])
