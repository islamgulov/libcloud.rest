# -*- coding:utf-8 -*-
from __future__ import with_statement
import unittest2
import httplib

try:
    import simplejson as json
except ImportError:
    import json

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
import libcloud
from libcloud.test.storage.test_cloudfiles import CloudFilesMockHttp,\
    CloudFilesMockRawResponse

from libcloud_rest.api.versions import versions as rest_versions
from libcloud_rest.application import LibcloudRestApp
from libcloud_rest.errors import NoSuchContainerError, \
    ContainerAlreadyExistsError, InvalidContainerNameError


class RackspaceUSTests(unittest2.TestCase):
    def setUp(self):
        self.url_tmpl = rest_versions[libcloud.__version__] +\
            '/storage/CLOUDFILES_US/%s?test=1'
        self.client = Client(LibcloudRestApp(), BaseResponse)
        self.headers = {'x-auth-user': 'user', 'x-api-key': 'key'}
        CloudFilesMockHttp.type = None
        CloudFilesMockRawResponse.type = None

    def test_list_containers(self):
        CloudFilesMockHttp.type = 'EMPTY'
        url = self.url_tmpl % ('containers')
        resp = self.client.get(url, headers=self.headers)
        containers = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertEqual(len(containers), 0)

        CloudFilesMockHttp.type = None
        url = self.url_tmpl % ('containers')
        resp = self.client.get(url, headers=self.headers)
        containers = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertEqual(len(containers), 3)

        container = [c for c in containers if c['name'] == 'container2'][0]
        self.assertEqual(container['extra']['object_count'], 120)
        self.assertEqual(container['extra']['size'], 340084450)

    def test_get_container(self):
        url = self.url_tmpl % ('/'.join(['containers', 'test_container']))
        resp = self.client.get(url, headers=self.headers)
        container = json.loads(resp.data)
        self.assertEqual(container['name'], 'test_container')
        self.assertEqual(container['extra']['object_count'], 800)
        self.assertEqual(container['extra']['size'], 1234568)
        self.assertEqual(resp.status_code, httplib.OK)

    def test_get_container_not_found(self):
        url = self.url_tmpl % ('/'.join(['containers', 'not_found']))
        resp = self.client.get(url, headers=self.headers)
        resp_data = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.NOT_FOUND)
        self.assertEqual(resp_data['error']['code'], NoSuchContainerError.code)

    def test_create_container_success(self):
        url = self.url_tmpl % ('containers')
        request_data = {'container_name': 'test_create_container'}
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(request_data),
                                content_type='application/json')
        container = json.loads(resp.data)
        self.assertEqual(container['name'], 'test_create_container')
        self.assertEqual(container['extra']['object_count'], 0)

    def test_create_container_already_exists(self):
        CloudFilesMockHttp.type = 'ALREADY_EXISTS'
        url = self.url_tmpl % ('containers')
        request_data = {'container_name': 'test_create_container'}
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(request_data),
                                content_type='application/json')
        result = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.CONFLICT)
        self.assertEqual(result['error']['code'],
                         ContainerAlreadyExistsError.code)

    def test_create_container_invalid_name_too_long(self):
        name = ''.join(['x' for x in range(0, 257)])
        url = self.url_tmpl % ('containers')
        request_data = {'container_name': name}
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(request_data),
                                content_type='application/json')
        result = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.BAD_REQUEST)
        self.assertEqual(result['error']['code'],
                         InvalidContainerNameError.code)

    def test_create_container_invalid_name_slashes_in_name(self):
        name = 'test/slahes/'
        url = self.url_tmpl % ('containers')
        request_data = {'container_name': name}
        resp = self.client.post(url, headers=self.headers,
                                data=json.dumps(request_data),
                                content_type='application/json')
        result = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.BAD_REQUEST)
        self.assertEqual(result['error']['code'],
                         InvalidContainerNameError.code)
