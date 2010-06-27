#!/usr/bin/python

"""
    SpringCl config object

        reads from, or update to springcl config file
"""
__all__ = ['Config']

import ConfigParser

class Config:
    DEFAULT_CONF_FILE = '~/.springcl/config'
    def __init__(self, conf_files=None):
        self.conf_files = conf_files or self.DEFAULT_CONF_FILE
        if '__len__' not in dir(self.conf_files):
            self.conf_files = [self.conf_files]

        self.parser = ConfigParser.SafeConfigParser()

    def load(self):
        self.parser.read(self.conf_files)

    def save(self):
        pass

    def get(self, option, section=None, default=None, type=None):
        # match type
        if   type is int:   get_func = self.parser.getint
        elif type is float: get_func = self.parser.getfloat
        elif type is bool:  get_func = self.parser.getboolean
        else:               get_func = self.parser.get

        # guess section name
        if section is None:
            sections = L(self.parser.sections()).filter(lambda section:
                self.parser.has_option(section, option)
            )
            if len(sections) > 1:
                raise "found multiple '%(option)s' from %(sections)s" % locals()
            elif len(sections) == 0:
                if self.parser.has_option('DEFAULT', option):
                    sections = ['DEFAULT']
                else:
                    raise "no such option: %(option)s" % locals()
            section = sections[0]
        
        # fetch value
        try:
            return get_func(section, option)
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            if default is not None:
                return default
            else:
                raise "no such option: %(option)s" % locals()
    def __getitem__(self, index):
        return self.get(option=index)


