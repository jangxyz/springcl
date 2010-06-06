#!/usr/bin/python
from springcl_options import SpringclOption
from springcl_commands import CONSUMER_TOKEN, CONSUMER_SECRET

class GlobalOptions(SpringclOption):
    options = '''
        --output FILE[None] : output file
        --note NOTE         : specify note name to delete resource on

        --local       => run_remote_on_fail[False]  : local first, remote only when failed
        --remote      => run_local_on_fail [False]  : remote first, local only when failed
        --local-only  => run_local         [False]  : always fetch resource locally
        --remote-only => run_remote        [False]  : always fetch resource remotely

        --auth     TOKSEC                                       : use TOKSEC as access token (in TOKEN:SECRET format)
        --consumer TOKSEC => [(CONSUMER_TOKEN,CONSUMER_SECRET)] : use TOKSEC as consumer token
    '''

    @classmethod
    def _build_parser(cls, parser=None):
        parser = parser or optparse.OptionParser()

        #parser.add_option('--basedir', metavar="PATH", default=BASE_PATH, dest="basedir", help='use PATH as local cache basedir')
        parser.add_option('--output', metavar="FILE", default=None, help='output file')
        #
        parser.add_option('--note', metavar='NOTE', help='specify note name to delete resource on')

        # local/remote
        def add_lr_opt(parser, *args, **kwargs):
            kwargs.update(default=False, action="callback", 
                callback=GlobalOptions.handle_local_remote)
            parser.add_option(*args, **kwargs)
        add_lr_opt(parser, '--local',       dest="run_remote_on_fail", help="local first, remote only when failed")
        add_lr_opt(parser, '--remote',      dest="run_local_on_fail",  help="remote first, local only when failed")
        add_lr_opt(parser, '--local-only',  dest="run_local",  help="always fetch resource locally")
        add_lr_opt(parser, '--remote-only', dest="run_remote", help="always fetch resource remotely")

        # auth
        def add_toksec_opt(parser, *args, **kwargs):
            kwargs.update(metavar="TOKSEC", type=str, action="callback", 
                callback=GlobalOptions.split_by_colon)
            parser.add_option(*args, **kwargs)
        add_toksec_opt(parser, '--auth',     help='use TOKSEC as access token (in TOKEN:SECRET format)')
        add_toksec_opt(parser, '--consumer', default=(CONSUMER_TOKEN, CONSUMER_SECRET), help='use TOKSEC as consumer token')

        return parser

    @staticmethod
    def split_by_colon(option, opt_str, value, parser, *args, **kwargs):
        dest = option.dest or opt_str.lstrip('-')
        setattr(parser.values, dest, tuple(value.split(':')))

    @staticmethod
    def handle_local_remote(option, opt_str, value, parser, *args, **kwargs):
        ''' handle run_local/run_remote/run_local_on_fail/run_remote_on_fail '''
        mapping = {
            '--local-only' : ('run_local' ,                      ),
            '--remote-only': ('run_remote',                      ),
            '--local'      : ('run_local' , 'run_remote_on_fail' ),
            '--remote'     : ('run_remote', 'run_local_on_fail'  ),
        }
        for attr in mapping[opt_str]:
            setattr(parser.values, attr, True)

        if parser.values.run_remote and parser.values.run_local:
            raise optparse.OptionValueError("can't use --local and --remote together")

