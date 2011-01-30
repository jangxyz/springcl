#!/usr/bin/python

import sys, types

from config import *
import springcl_commands

from util import *

command_dict = {}
# dynamically load every subclass of class SpringclCommand
for class_name in springcl_commands.__all__:
    command_name = springcl_commands.classname2commandname(class_name)
    command_dict[command_name] = getattr(springcl_commands, class_name)

# dynamicaly bind methods
for k,v in command_dict.iteritems():
    locals()[k] = v

# tmp
#locals()['init'] = lambda *args: args


def camel2sentence(camel):
    return ''.join([' %s' % letter.lower() if letter.isupper() else letter for letter in camel]).strip()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        commands = [cmd_name for cmd_name in command_dict if '-' not in cmd_name]
        print 'commands:', ", ".join(commands)
        commands = [cmd_name for cmd_name in command_dict if '-' in cmd_name]
        print 'more commands:', ", ".join(commands)
        sys.exit()

    try:
        cmd = command_dict.get(sys.argv[1], None)
        if cmd is not None:
            arg = sys.argv[1]
            cmd(sys.argv[2:]).run()
        #except springcl_commands.Errors.OptionError:
        #    print cmd.usage()

        #except Exception, e:
        #    msg = camel2sentence(e.__class__.__name__)
        #    if e.message:
        #        msg += ": %s" % e.message
        #    sys.exit(msg)
    finally:
        pass

