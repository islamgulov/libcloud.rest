# -*- coding:utf-8 -*-


class BaseDriverPatch(object):
    def postprocess(self, driver):
        pass

    def preprocess(self, Driver):
        pass


class ConnClassDriverPatch(BaseDriverPatch):
    def __init__(self, http, https):
        self.conn_classes = (http, https)

    def preprocess(self, Driver):
        Driver.connectionCls.conn_classes = self.conn_classes
