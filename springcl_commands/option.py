#!/usr/bin/python
'''
    in-house Option/Parser library wrapping optparse module to use simple syntax
    such as 
        --attachment => is_attachment[False] : delete attachment (default is page)
        --parent ID  => parent_id<int>       : parent page id (only for attachment)

    Syntax:
        LINE = OPT [DEST] [HELP] 

        OPT  = --longopt [metavar]

        DEST = => dest_var 
               => dest_var \[dest_default_value\]
               => dest_var <dest_type>

        HELP = ": help_message"
'''
import optparse


class Option:
    opt  = None
    dest = None
    help = None

    @classmethod
    def build(cls, line):
        ''' returns tuple of (parsed result, remaining line) '''
        result = Option()

        if ':' in line:
            line, help_line = line.split(':', 1)
            result.help = Help.build(':' + help_line)

        if '=>' in line:
            line, dest_line = line.split('=>', 1)
            result.dest = Dest.build('=>' + dest_line)

        if '-' in line:
            result.opt = Opt.build(line)

        return result

    @classmethod
    def build_from(self, usage=None, options=None, groups=None):
        pass


class Opt:  
    ''' OPT = "--LONGOPT [METAVAR]" : long, metavar '''
    long, metavar = None, None

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
    ''' DEST = "=> DEST_VAR "                      : varname
               "=> DEST_VAR <DEST_TYPE>"           : varname, type
               "=> DEST_VAR [DEST_DEFAULT_VALUE]"  : varname, type, default value
    '''
    varname, type, default = None, None, None
    supported = [bool, int, long, str, float]

    @classmethod
    def build(cls, line):
        line = line.strip()

        new_dest = Dest()
        if line.startswith('=>'):
            line = line.partition('=>')[-1].strip()

            # [DEFAULT_VALUE] (ex. [True], [123])
            if cls._is_surrounded_by(line, '[', ']'):
                new_dest.varname = line.split(' ', 1)[0].split('[', 1)[0]
                line = line.partition(new_dest.varname)[-1].strip()

                new_dest.default = eval(cls._strip_surrounding(line, '[', ']'))
                new_dest.type    = type(new_dest.default)
                
            # <TYPE> (ex. <str>, <int>)
            elif cls._is_surrounded_by(line, '<', '>'):
                new_dest.varname = line.split(' ', 1)[0].split('<', 1)[0]
                line = line.partition(new_dest.varname)[-1].strip()

                type_name = cls._strip_surrounding(line, '<', '>')
                if type_name in map(lambda x: x.__name__, cls.supported):
                    new_dest.type = eval(type_name)

            # nothing
            else:
                new_dest.varname = line.split(' ', 1)[0]
                line = line.partition(new_dest.varname)[-1].strip()

        return new_dest

    @classmethod
    def _is_surrounded_by(cls, line, prefix, suffix):
        prefix_idx = line.find(prefix)
        suffix_idx = line.find(suffix)
        return prefix_idx != -1 and suffix_idx != -1 and prefix_idx < suffix_idx

    @classmethod
    def _strip_surrounding(cls, line, prefix, suffix):
        prefix_idx = line.find(prefix)
        suffix_idx = line.find(suffix)
        assert prefix_idx != -1 and suffix_idx != -1 and prefix_idx < suffix_idx

        return line[prefix_idx+1 : suffix_idx]

        


class Help: 
    ''' HELP = ": HELP_MESSAGE" '''
    msg = ''

    @classmethod
    def build(cls, line):
        line = line.strip()

        new_help = Help()

        if line.strip().startswith(':'):
            line = line.partition(':')[-1].strip()

            new_help.msg = line.strip()
            line = line.partition(new_help.msg)[-1].strip()

        return new_help


class Parser:
    def __init__(self, usage=None, options=None, groups=[]):
        self.usage  = usage.strip()
        self.groups = groups
        
        self.options = []
        for option_str in options.strip().split("\n"):
            option = Option.build(option_str)
            self.options.append(option)

    def _build(self):
        ''' bulids option parser '''
        parser = optparse.OptionParser(usage=self.usage)

        for option in self.options:
            args, kwargs = [], {}

            if option.opt:
                if option.opt.long is not None:
                    args.append('--' + option.opt.long)
                if option.opt.metavar is not None:
                    kwargs['metavar'] = option.opt.metavar

            if option.dest:
                if option.dest.varname is not None:
                    kwargs['dest'] = option.dest.varname
                if option.dest.default is not None:
                    kwargs['default'] = option.dest.default
                if option.dest.type is not None:
                    # bool is different
                    if option.dest.type is bool:
                        default = option.dest.default
                        kwargs['action'] = 'store_' + `not default`.lower()
                    else:
                        kwargs['type'] = option.dest.type

            if option.help and option.help.msg is not None:
                kwargs['help'] = option.help.msg

            parser.add_option(*args, **kwargs)

        # option groups
        for group in self.groups:
            option_group = optparse.OptionGroup(parser, group.title)
            group._build_parser(option_group)
            parser.add_option_group(option_group)

        return parser


    def parse(self, args):
        ''' parse input '''
        parser = self._build()
        options, args = parser.parse_args(args)
        options.args = args
        return options


