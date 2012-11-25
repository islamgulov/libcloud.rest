# -*- coding:utf-8 -*-
from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase


class Request(RequestBase):
    url_rule = None
    args = None

    @property
    def handler(self):
        """
        The name of current handler
        """
        if self.url_rule and '.' in self.url_rule.endpoint:
            return self.url_rule.endpoint.rsplit('.', 1)[0]

    def endpoint(self):
        if self.url_rule is not None:
            self.url_rule.endpoint


class Response(ResponseBase):
    default_mimetype = 'application/json'
