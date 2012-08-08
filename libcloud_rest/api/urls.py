# -*- coding:utf-8 -*-
from werkzeug.routing import Map, Rule, Submount, RuleTemplate, RuleFactory
import libcloud

from libcloud_rest.api.handlers import ApplicationHandler, ComputeHandler,\
    DNSHandler, StorageHandler, LoadBalancerHandler
from libcloud_rest.api.versions import versions

api_version = '/%s' % (versions[libcloud.__version__])


class HandlerEndpoint(RuleFactory):
    def __init__(self, path, handler, rules):
        self.path = path.rstrip('/')
        self.handler = handler
        self.rules = rules

    def get_rules(self, map):
        for rulefactory in self.rules:
            for rule in rulefactory.get_rules(map):
                rule = rule.empty()
                rule.rule = self.path + rule.rule
                rule.endpoint = (self.handler, rule.endpoint)
                yield rule

providers_list_rule = Rule(
    '/providers', endpoint='providers',
    methods=['GET'])

provider_info_rule = Rule(
    '/providers/<string:provider_name>',
    endpoint='provider_info', methods=['GET'])

extra_method_rule = Rule('/<string:provider>/<string:method_name>',
                         endpoint='invoke_method', methods=['POST'])

list_objects_rule_template = RuleTemplate([Rule(
    '/<string:provider>/$objects', defaults={'method_name': 'list_$objects'},
    endpoint='invoke_method', methods=['GET'])])

compute_urls = HandlerEndpoint('/compute', ComputeHandler, [
    providers_list_rule,
    provider_info_rule,
    extra_method_rule,
    list_objects_rule_template(objects='nodes'),
    list_objects_rule_template(objects='images'),
    list_objects_rule_template(objects='sizes'),
    list_objects_rule_template(objects='locations'),
    Rule('/<string:provider>/nodes', defaults={'method_name': 'create_node'},
         endpoint='create_node', methods=['POST']),
    Rule('/<string:provider>/nodes/<string:node_id>/reboot',
         endpoint='reboot_node',
         methods=['POST']),
    Rule('/<string:provider>/nodes/<string:node_id>',
         endpoint='destroy_node',
         methods=['DELETE']),
])

storage_urls = HandlerEndpoint('/storage', StorageHandler, [
    providers_list_rule,
])

loadbalancer_urls = HandlerEndpoint('/loadbalancer', LoadBalancerHandler, [
    providers_list_rule,
    provider_info_rule,
    extra_method_rule,
    list_objects_rule_template(objects='protocols'),
    list_objects_rule_template(objects='balancers'),
    Rule('/<string:provider>/algorithms',
         endpoint='invoke_method',
         defaults={'method_name': 'list_supported_algorithms'},
         methods=['GET']),
    Rule('/<string:provider>/balancers',
         defaults={'method_name': 'create_balancer'},
         endpoint='create_balancer', methods=['POST']),
    Rule('/<string:provider>/balancers/<string:loadbalancer_id>',
         endpoint='destroy_balancer', methods=['DELETE'],
         defaults={'method_name': 'destroy_balancer'}),
    Rule('/<string:provider>/balancers/<string:loadbalancer_id>',
         endpoint='patch_request_and_invoke', methods=['PUT'],
         defaults={'method_name': 'update_balancer'}),
    Rule('/<string:provider>/balancers/<string:balancer_id>',
         endpoint='get_balancer',
         defaults={'method_name': 'get_balancer'},
         methods=['GET']),
    Rule('/<string:provider>/balancers/<string:loadbalancer_id>/members',
         defaults={'method_name': 'balancer_list_members'},
         endpoint='patch_request_and_invoke', methods=['GET']),
    Rule('/<string:provider>/balancers/<string:loadbalancer_id>/members',
         defaults={'method_name': 'balancer_attach_member'},
         endpoint='patch_request_and_invoke', methods=['POST']),
    Rule('/<string:provider>/balancers/<string:loadbalancer_id>/'
         'members/<string:member_id>',
         defaults={'method_name': 'balancer_detach_member'},
         endpoint='detach_member', methods=['DELETE']),
])

dns_urls = HandlerEndpoint('/dns', DNSHandler, [
    providers_list_rule,
    Rule('/<string:provider>/zones', endpoint='list_zones',
         methods=['GET']),
    Rule('/<string:provider>/zones/<string:zone_id>/records',
         endpoint='list_records', methods=['GET']),
    Rule('/<string:provider>/zones', endpoint='create_zone',
         methods=['POST']),
    Rule('/<string:provider>/zones/<string:zone_id>',
         endpoint='update_zone', methods=['PUT']),
    Rule('/<string:provider>/zones/<string:zone_id>',
         endpoint='delete_zone', methods=['DELETE']),
    Rule('/<string:provider>/zones/<string:zone_id>'
         '/records/<string:record_id>',
         endpoint='get_record', methods=['GET']),
    Rule('/<string:provider>/zones/<string:zone_id>/records',
         endpoint='create_record', methods=['POST']),
    Rule('/<string:provider>/zones/<string:zone_id>/'
         'records/<string:record_id>',
         endpoint='update_record', methods=['PUT']),
    Rule('/<string:provider>/zones/<string:zone_id>/'
         'records/<string:record_id>',
         endpoint='delete_record', methods=['DELETE']),
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
