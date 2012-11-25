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

    @cached_property
    def json(self):
        """If the mimetype is `application/json` this will contain the
        parsed JSON data.  Otherwise this will be `None`.

        This requires Python 2.6 or an installed version of simplejson.
        """
        if self.mimetype == 'application/json':
            try:
                return json.loads(self.data)
            except (ValueError, TypeError), e:
                raise MalformedJSONError(detail=str(e))


class Response(ResponseBase):
    default_mimetype = 'application/json'
