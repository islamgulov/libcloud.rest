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
from libcloud.storage.drivers.cloudfiles import CloudFilesUSStorageDriver
from libcloud.storage.base import Container, Object
from mock import patch

from libcloud_rest.api.versions import versions as rest_versions
from libcloud_rest.application import LibcloudRestApp
from libcloud_rest.errors import NoSuchContainerError, \
    ContainerAlreadyExistsError, InvalidContainerNameError,\
    ContainerIsNotEmptyError, NoSuchObjectError


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
        self.assertEqual(resp.status_code, httplib.CREATED)

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

    def test_delete_container_success(self):
        url = self.url_tmpl % ('/'.join(['containers', 'foo_bar_container']))
        resp = self.client.delete(url, headers=self.headers)
        self.assertEqual(resp.status_code, httplib.NO_CONTENT)

    def test_delete_container_not_found(self):
        CloudFilesMockHttp.type = 'NOT_FOUND'
        url = self.url_tmpl % ('/'.join(['containers', 'foo_bar_container']))
        resp = self.client.delete(url, headers=self.headers)
        result = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.NOT_FOUND)
        self.assertEqual(result['error']['code'], NoSuchContainerError.code)

    def test_delete_container_not_empty(self):
        CloudFilesMockHttp.type = 'NOT_EMPTY'
        url = self.url_tmpl % ('/'.join(['containers', 'foo_bar_container']))
        resp = self.client.delete(url, headers=self.headers)
        result = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.BAD_REQUEST)
        self.assertEqual(result['error']['code'],
                         ContainerIsNotEmptyError.code)

    def test_list_container_objects(self):
        CloudFilesMockHttp.type = 'EMPTY'
        url = self.url_tmpl % (
            '/'.join(['containers', 'test_container', 'objects']))
        resp = self.client.get(url, headers=self.headers)
        objects = json.loads(resp.data)
        self.assertEqual(len(objects), 0)
        self.assertEqual(resp.status_code, httplib.OK)

        CloudFilesMockHttp.type = None
        resp = self.client.get(url, headers=self.headers)
        objects = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertEqual(len(objects), 4)

        obj = [o for o in objects if o['name'] == 'foo test 1'][0]
        self.assertEqual(obj['hash'], '16265549b5bda64ecdaa5156de4c97cc')
        self.assertEqual(obj['size'], 1160520)
        self.assertEqual(obj['container']['name'], 'test_container')

    def test_get_object_success(self):
        url = self.url_tmpl % (
            '/'.join(['containers', 'test_container',
                      'objects', 'test_object']))
        resp = self.client.get(url, headers=self.headers)
        obj = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertEqual(obj['container']['name'], 'test_container')
        self.assertEqual(obj['size'], 555)
        self.assertEqual(obj['hash'], '6b21c4a111ac178feacf9ec9d0c71f17')
        self.assertEqual(obj['extra']['content_type'], 'application/zip')
        self.assertEqual(
            obj['extra']['last_modified'], 'Tue, 25 Jan 2011 22:01:49 GMT')
        self.assertEqual(obj['meta_data']['foo-bar'], 'test 1')
        self.assertEqual(obj['meta_data']['bar-foo'], 'test 2')

    def test_get_object_not_found(self):
        url = self.url_tmpl % (
            '/'.join(['containers', 'test_container',
                      'objects', 'not_found']))
        resp = self.client.get(url, headers=self.headers)
        result = json.loads(resp.data)
        self.assertEqual(resp.status_code, httplib.NOT_FOUND)
        self.assertEqual(result['error']['code'],
                         NoSuchObjectError.code)

    def test_download_object(self):
        url = self.url_tmpl % (
            '/'.join(['containers', 'foo_bar_container',
                      'objects', 'foo_bar_object', 'download']))
        container = Container(name='foo_bar_container', extra={}, driver=None)
        obj = Object(name='foo_bar_object', size=1000, hash=None, extra={},
                     container=container, meta_data=None,
                     driver=None)

        with patch.object(CloudFilesUSStorageDriver, 'get_object',
                          mocksignature=True) as get_object_mock:
            get_object_mock.return_value = obj
            resp = self.client.get(url, headers=self.headers)
        self.assertEqual(resp.status_code, httplib.OK)
