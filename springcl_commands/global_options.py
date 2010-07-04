#!/usr/bin/python
import env
from util import *

from springcl_commands import CONSUMER_TOKEN, CONSUMER_SECRET
from config import *

import optparse

config = Config().load()

class GlobalOptions:
    options = '''
        --basedir PATH[BASE_PATH] => basedir : use PATH as local cache basedir

        # resource
        --note NOTE         : specify note name to delete resource on
        --output FILE[None] : output file

        # source local / remote
        --local-soft  => run_remote_on_fail : local first, remote only when failed
        --remote-soft => run_local_on_fail  : remote first, local only when failed
        --local-only  => run_local          : always fetch resource locally
        --remote-only => run_remote         : always fetch resource remotely
        --local                             : local, then follow conf file setting
        --remote                            : remote, then follow conf file setting

        # auth
        --auth     TOKSEC                                       : use TOKSEC as access token (in TOKEN:SECRET format)
        --consumer TOKSEC => [(CONSUMER_TOKEN,CONSUMER_SECRET)] : use TOKSEC as consumer token
    '''

    @classmethod
    def _build_parser(cls, parser=None):
        parser = parser or optparse.OptionParser()

        parser.add_option('--basedir', metavar="PATH", default=None, dest="basedir", help='use PATH as local cache basedir')
        parser.add_option('--output', metavar="FILE", default=None, help='output file')
        #
        parser.add_option('--note', metavar='NOTE', help='specify note name to delete resource on')

        # source local/remote - use callback
        parser.add_option('--local-soft',  dest="run_remote_on_fail", help="try local first, then remote only when necessary", action="callback", callback=handle_local_remote)
        parser.add_option('--local-only',  dest="run_local",          help="always fetch resource locally",        action="callback", callback=handle_local_remote)
        parser.add_option('--remote-soft', dest="run_local_on_fail",  help="try remote first, then local only when necessary", action="callback", callback=handle_local_remote)
        parser.add_option('--remote-only', dest="run_remote",         help="always fetch resource remotely",       action="callback", callback=handle_local_remote)
        parser.add_option('--local',  help="local, then follow conf file setting", action="callback", callback=handle_local_remote)
        parser.add_option('--remote', help="remote, then follow conf file setting", action="callback", callback=handle_local_remote)

        # auth
        parser.add_option('--consumer', default=(CONSUMER_TOKEN, CONSUMER_SECRET), help='use TOKSEC as consumer token',                        metavar="TOKSEC", type=str, action="callback", callback=split_by_colon)
        parser.add_option('--auth', help='use TOKSEC as access token (in TOKEN:SECRET format)', 
            metavar  = "TOKSEC",
            type     = str,
            action   = "callback",
            callback = split_by_colon)

        return parser

def split_by_colon(option, opt_str, value, parser, *args, **kwargs):
    dest = option.dest or opt_str.lstrip('-')
    setattr(parser.values, dest, tuple(value.split(':')))


def handle_local_remote(option, opt_str, value, parser, *args, **kwargs):
    ''' handle run_local/run_remote/run_local_on_fail/run_remote_on_fail.
    raises error if more than one option is given.
    '''
    for attr in _w('run_local run_remote run_local_on_fail run_remote_on_fail'):
        if not hasattr(parser.values, attr):
            setattr(parser.values, attr, None)

    is_source_only = config['source-only']

    mapping = {
        '--local-only' : ('run_local' ,                      ),
        '--local-soft' : ('run_local' , 'run_remote_on_fail' ),
        '--local'      : (),
        '--remote-only': ('run_remote',                      ),
        '--remote-soft': ('run_remote', 'run_local_on_fail'  ),
        '--remote'     : (),
    }
    suffix = '-only' if is_source_only else '-soft'
    mapping['--local' ] = mapping['--local'  + suffix]
    mapping['--remote'] = mapping['--remote' + suffix]

    # set True
    for attr in mapping[opt_str]:
        setattr(parser.values, attr, True)
    # set False
    false_options = filter(lambda opt: opt not in mapping[opt_str], set(reduce(lambda x,y: x+y, mapping.values())))
    for attr in false_options :
        setattr(parser.values, attr, False)

    # check duplicate
    if parser.values.run_remote and parser.values.run_local:
        raise optparse.OptionValueError("can't use --local and --remote together")


