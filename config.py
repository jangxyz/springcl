#!/usr/bin/python

"""
    SpringCl config object

        reads from, or update to springcl config file
"""
__all__ = ['Config']

import ConfigParser
from util import *


class ValueNotGiven: pass
class Config:
    #DEFAULT_CONF_FILE = '~/.springcl/config'
    DEFAULT_CONF_FILE = 'sample_conf'
    def __init__(self, conf_files=None):
        self.conf_files = None
        self.conf_files = self._get_conf_files(conf_files)
        self.parser = ConfigParser.SafeConfigParser()

    def _get_conf_files(self, _conf_files):
        conf_files = _conf_files or self.conf_files or self.DEFAULT_CONF_FILE
        if '__len__' not in dir(conf_files):
            conf_files = [conf_files]
        return conf_files

    def load(self, conf_files=None):
        ''' read conf file '''
        self.conf_files = self._get_conf_files(conf_files)
        self.parser.read(self.conf_files)

        return self

    def save(self):
        ''' write to conf file '''
        print 'NOT YET'
        pass

    def get(self, option, section=None, default=ValueNotGiven, type=None):
        # match type
        if   type is int:   get_func = self.parser.getint
        elif type is float: get_func = self.parser.getfloat
        elif type is bool:  get_func = self.parser.getboolean
        else:               get_func = self.parser.get

        # guess section name
        if section is None:
            sections = self._sections_with_option(option)
            if len(sections) > 1:
                raise "found multiple '%(option)s' from %(sections)s" % locals()
            if len(sections) == 0:
                if default is not ValueNotGiven:
                    return default
                raise "no such option: %(option)s" % locals()
            section = sections[0]
        
        # fetch value
        try:
            return get_func(section, option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            if default is not ValueNotGiven:
                return default
            else:
                raise "no such option: %(option)s" % locals()
    def __getitem__(self, index):
        return self.get(option=index)

    def _sections_with_option(self, option, section=None):
        opt_in = lambda section: self.parser.has_option(section, option)
        # check DEFAULT first
        if opt_in('DEFAULT'):
            return L(['DEFAULT'])

        # find from any other sections
        if section is None: sections = self.parser.sections()
        else:               sections = [section]
        return L(sections).filter(lambda section: opt_in(section))

    def has(self, option, section=None):
        return len(self._sections_with_option(option, section)) > 0

    def to_dict(self):
        for section in self.parser.sections():
            print section
            for option in self.parser.options(section):
                print '\t', option
        

        # {section1: {option1: value1, option2: value2}, section2: {}}
        return dict(L(self.parser.sections()).map(lambda section:
            # (section1, {option1: value1, option2: value2})
            (section, dict(L(self.parser.options(section)).map(lambda option:
                # (option1, value1)
                (option, self.parser.get(section, option))
            )))
        ))


if __name__ == '__main__':
    print Config().load().to_dict()


