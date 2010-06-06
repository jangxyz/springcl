#!/usr/bin/python
from springcl_commands import *
import optparse

class SpringclOption:
    _parser = None

    @classmethod
    def _build_parser(cls, parser=None):
        raise NotImplementedError("inherit this class")

    @classmethod
    def parser(cls):
        if cls._parser is None:
            cls._parser = cls._build_parser()
        return cls._parser
        
    @classmethod
    def parse(cls, opt_list):
        options, args = cls.parser().parse_args(opt_list)
        options.args = args
        return options

