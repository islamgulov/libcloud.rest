# -*- coding:utf-8 -*-
from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase
from werkzeug.utils import cached_property

from libcloud_rest.utils import json
from libcloud_rest.errors import MalformedJSONError


class Request(RequestBase):
    url_rule = None
    args = None

    @property
    def handler_class(self):
        if self.url_rule is not None:
            return self.url_rule[0]

    @property
    def action(self):
        if self.url_rule is not None:
            return  self.url_rule[1]


class Response(ResponseBase):
    default_mimetype = 'application/json'
