#!/usr/bin/python
'''
    in-house Option/Parser library wrapping optparse module to use simple syntax
    such as
        --attachment => is_attachment[False] : delete attachment (default is page)
        --parent ID  => parent_id<int>       : parent page id (only for attachment)

        [Global Options]

    Syntax ([] is optional. \[ and \] represents actual "[" and "]"):
        LINE = OPT [DEST] [HELP]
               GROUP
               # comment
        OPT   = --longopt [metavar]
        DEST  = => dest_var 
                => dest_var \[dest_default_value\]
                => dest_var <dest_type>
        HELP  = : help_message
        GROUP = \[group_name\]
#'''
import optparse, types


def is_surrounded_by(line, prefix, suffix):
    prefix_idx = line.find(prefix)
    suffix_idx = line.find(suffix)
    return prefix_idx != -1 and suffix_idx != -1 and prefix_idx < suffix_idx

def strip_surrounding(line, prefix, suffix):
    prefix_idx = line.find(prefix)
    suffix_idx = line.find(suffix)
    assert prefix_idx != -1 and suffix_idx != -1 and prefix_idx < suffix_idx

    return line[prefix_idx+1 : suffix_idx]

class BaseOption: pass

class NullOption(BaseOption):
    def __str__(self): return ''
    def add_option(self, parser):
        pass

class Option(BaseOption):
    opt  = NullOption()
    dest = NullOption()
    help = NullOption()

    def __str__(self):
        return ' '.join(map(str, (self.opt, self.dest, self.help)))

    @classmethod
    def build(cls, line):
        ''' factory method. builds instance of BaseOption from line given.
        
        1.  --OPT [=> DEST] [: HELP]
        2.  \[GROUP\]
        3.  # comment
        '''
        line = line.strip()

        if line.startswith('#'):
            line = line.partition('#')[0]
        if line.strip() == '':
            return NullOption()

        help_line, dest_line, opt_line, group_line = None, None, None, None
        # --OPT [=> DEST] [: HELP]
        if line.startswith('-'):
            if ':'  in line:  line, help_line = line.split(':',  1) 
            if '=>' in line:  line, dest_line = line.split('=>', 1)
            opt_line = line 
        # \[GROUP\]
        elif is_surrounded_by(line, '[', ']'):
            group_line = line

        if opt_line:  
            result = Option()
            result.opt = Opt.build(opt_line)
            if dest_line: result.dest = Dest.build('=>' + dest_line, result.opt.long)
            if help_line: result.help = Help.build(':' + help_line)
        elif group_line:
            return GroupOption.build(group_line)

        return result

    def add_option(self, parser):
        args, kwargs = [], {}

        is_valid = lambda x: x is not None
        if self.opt:
            # opt
            if is_valid(self.opt.long):
                args.append('--' + self.opt.long)
            # metavar
            if is_valid(self.opt.metavar):
                kwargs['metavar'] = self.opt.metavar

        if self.dest:
            # dest
            if   is_valid(self.dest.varname): kwargs['dest'] = self.dest.varname
            elif is_valid(self.opt.metavar):  kwargs['dest'] = self.opt.metavar

            # default
            if is_valid(self.dest.default):
                kwargs['default'] = self.dest.default
            # action, type
            if is_valid(self.dest.type):
                # bool is different
                if self.dest.type is bool:
                    default = self.dest.default
                    kwargs['action'] = 'store_' + `not default`.lower()
                else:
                    kwargs['type'] = self.dest.type

        if self.help and is_valid(self.help.msg):
            kwargs['help'] = self.help.msg

        parser.add_option(*args, **kwargs)


class Opt:  
    ''' OPT = "--LONGOPT [METAVAR]" : long, metavar '''
    long, metavar = None, None

    def __str__(self):
        s = []
        if self.long:    s.append('--' + self.long)
        if self.metavar: s.append(self.metavar)
        return ' '.join(s)

    @classmethod
    def build(cls, line):
        line = line.strip()

        result = Opt()
        if line.startswith('--'):
            result.long = line.split()[0].strip('-')
            line = line.partition(result.long)[-1].strip()

        if len(line) > 0:
            result.metavar = line

        return result

class Dest: 
    ''' DEST = "=> [DEST_VAR] [<DEST_TYPE>] [\[DEST_DEFAULT_VALUE\]]" 
        : varname, type, default
    '''
    varname, type, default = None, None, None
    supported = [bool, int, long, str, float]

    def __str__(self):
        s = ["=>"]
        if self.varname: s.append(self.varname)
        if self.type:    s.append("<%s>" % self.type.__name__)
        if self.default: s.append("[%s]" % str(self.default))
        return ' '.join(s)

    @classmethod
    def build(cls, line, opt_name):
        line = line.strip()

        new_dest = Dest()
        if line.startswith('=>'):
            line = line.partition('=>')[-1].strip()

            # [DEFAULT_VALUE] (ex. [True], [123])
            if is_surrounded_by(line, '[', ']'):
                new_dest.varname = line.split('[', 1)[0].split(' ', 1)[0]
                if new_dest.varname:
                    line = line.partition(new_dest.varname)[-1].strip()

                new_dest.default = eval(strip_surrounding(line, '[', ']'))
                new_dest.type    = type(new_dest.default)
                
            # <TYPE> (ex. <str>, <int>)
            elif is_surrounded_by(line, '<', '>'):
                new_dest.varname = line.split(' ', 1)[0].split('<', 1)[0]
                line = line.partition(new_dest.varname)[-1].strip()

                type_name = strip_surrounding(line, '<', '>')
                if type_name in map(lambda x: x.__name__, cls.supported):
                    new_dest.type = eval(type_name)

            # nothing
            else:
                new_dest.varname = line.split(' ', 1)[0]
                line = line.partition(new_dest.varname)[-1].strip()

            new_dest.varname = new_dest.varname or opt_name
        return new_dest

class Help: 
    ''' HELP = ": HELP_MESSAGE" '''
    msg = ''

    def __str__(self):
        s = [":"]
        if self.msg: 
            s.append(self.msg)
        return ' '.join(s)

    @classmethod
    def build(cls, line):
        line = line.strip()

        new_help = Help()

        if line.strip().startswith(':'):
            line = line.partition(':')[-1].strip()

            new_help.msg = line.strip()
            line = line.partition(new_help.msg)[-1].strip()

        return new_help

class GroupOption(BaseOption):
    name = None
    def __init__(self, group_name):
        self.name = strip_surrounding(group_name, '[', ']')

    @classmethod
    def build(self, group_name):
        return GroupOption(group_name)

    def add_option(self, parser):
        mod = __import__(self.name.replace(' ', '_').lower())
        cls = getattr(mod, self.name.replace(' ', ''))

        option_group = optparse.OptionGroup(parser, self.name)
        cls._build_parser(option_group)
        parser.add_option_group(option_group)

class Parser:
    def __init__(self, usage='', options=None, groups=[]):
        self.usage  = usage.strip()
        self.groups = groups
        
        self.options = []
        for option_str in options.strip().split("\n"):
            option = Option.build(option_str)
            self.options.append(option)

    def _build(self):
        ''' bulids option parser '''
        parser   = optparse.OptionParser(usage=self.usage)
        is_valid = lambda x: x is not None

        for option in self.options:
            option.add_option(parser)

            #args, kwargs = [], {}

            #if option.opt:
            #    # 
            #    if is_valid(option.opt.long):
            #        args.append('--' + option.opt.long)
            #    # metavar
            #    if is_valid(option.opt.metavar):
            #        kwargs['metavar'] = option.opt.metavar

            #if option.dest:
            #    # dest
            #    if   is_valid(option.dest.varname): kwargs['dest'] = option.dest.varname
            #    elif is_valid(option.opt.metavar):  kwargs['dest'] = option.opt.metavar

            #    # default
            #    if is_valid(option.dest.default):
            #        kwargs['default'] = option.dest.default
            #    # action, type
            #    if is_valid(option.dest.type):
            #        # bool is different
            #        if option.dest.type is bool:
            #            default = option.dest.default
            #            kwargs['action'] = 'store_' + `not default`.lower()
            #        else:
            #            kwargs['type'] = option.dest.type

            #if option.help and is_valid(option.help.msg):
            #    kwargs['help'] = option.help.msg

            #parser.add_option(*args, **kwargs)

        ## option groups
        #for group in self.groups:
        #    option_group = optparse.OptionGroup(parser, group.title)
        #    group._build_parser(option_group)
        #    parser.add_option_group(option_group)

        return parser

    def parse(self, args):
        ''' parse input '''
        parser = self._build()
        options, args = parser.parse_args(args)
        options.args = args
        return options


