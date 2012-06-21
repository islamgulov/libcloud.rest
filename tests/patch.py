# -*- coding:utf-8 -*-


class BaseDriverPatch(object):
    def post_process(self, driver):
        pass

    def pre_process(self, Driver):
        pass


class ConnClassDriverPatch(BaseDriverPatch):
    def __init__(self, http, https):
        self.conn_classes = (http, https)

    def pre_process(self, Driver):
        Driver.connectionCls.conn_classes = self.conn_classes
