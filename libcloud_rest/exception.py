# -*- coding:utf-8 -*-


class ValidationError(Exception):
    pass


class MissingArguments(Exception):

    def __init__(self, arguments):
        self.arguments = arguments

    def __str__(self):
        return "Missing arguments: %s" % str(self.arguments)
