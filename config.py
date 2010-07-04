#!/usr/bin/python

"""
    SpringCl config object

        reads from, or update to springcl config file
"""
__all__ = ['Config']

import ConfigParser
from util import *
from os.path import expanduser, expandvars, abspath
import types

list_of_options = _w('''
    basedir 
    source 
    source-only 
    default_note 
    consumer 
    auth
''')
default_options = {
    'basedir'     : '~/.springcl',
    'source'      : None,
    'source-only' : None,
    'default_note': None,
    'consumer'    : None,
    'auth'        : None,
}

class Config:
    DEFAULT_CONF_FILE = '~/.springcl/config'
    #DEFAULT_CONF_FILE = 'sample_conf'
    def __init__(self, conf_files=None):
        self.conf_files = self._get_conf_files(conf_files)
        self._config_dict = {}

    def _get_conf_files(self, _conf_files):
        conf_files = _conf_files or self.__dict__.get('conf_files', None) or self.DEFAULT_CONF_FILE
        if isinstance(conf_files, types.StringTypes):
            conf_files = [conf_files]

        return map(lambda x: abspath(expanduser(expandvars(x))), conf_files)

    def load(self, conf_files=None):
        ''' read conf file '''
        self.conf_files = self._get_conf_files(conf_files)
        parser = ConfigParser.SafeConfigParser()
        parser.read(self.conf_files)

        # set _config_dict
        for section in parser.sections():
            for option in parser.options(section):
                if not self._config_dict.get(option, None):
                    self._config_dict[option] = parser.get(section, option)

        # set default
        for option, value in default_options.iteritems():
            if option not in self._config_dict:
                self._config_dict[option] = value

        # process
        for option, value in self._config_dict.iteritems():
            self._config_dict[option] = self.process_value(value)

        return self

    @classmethod
    def process_value(cls, value):
        if isinstance(value, types.StringTypes):
            # strip off inline comments 'yes # blah blah'
            value = value.partition('#')[0].strip()
            # expand vars
            value = expanduser(expandvars(value))
        return value

    def save(self):
        ''' write to conf file '''
        print 'NOT YET'

    def get(self, option, eval=True, default=ValueNotGiven):
        if default is not ValueNotGiven:
            return self._config_dict.get(option, default)

        # fetch value
        value = self._config_dict[option]
        if eval:
            # int
            try: value = int(value)
            except ValueError: pass
            # float
            try: value = float(value)
            except ValueError: pass
            # boolean
            if   value in _w("yes true True "): value = True
            elif value in _w("no false False"): value = False
        return value
    def __getitem__(self, index): 
        return self.get(option=index)

    def to_dict(self):
        return self._config_dict


if __name__ == '__main__':
    print Config().load().to_dict()


