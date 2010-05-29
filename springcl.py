#!/usr/bin/python

import springcl_commands
import sys, types

command_dict = {}
# dynamically load every subclass of class SpringclCommand
for class_name in springcl_commands.__all__:
    command_name = springcl_commands.classname2commandname(class_name)
    command_dict[command_name] = getattr(springcl_commands, class_name)

##
## springcl constants
##
#class Command:
#    FETCH, COMMIT = 'fetch', 'commit'
#class OPTION:
#    class RESOURCE_SITE:
#        LOCAL, REMOTE, LOCAL_ONLY = 'local', 'remote', 'local-only'
#    class TARGET_TYPE:
#        TITLE, IDENTIFIER = 'title', 'identifier'
#
#def parse(arguments):
#    cmd         = None
#    access_key  = None
#    resource    = None
#    note        = None
#    target_type = None
#    target      = None
#
#    #
#    # options
#    #
#
#    # AUTHORIZATION
#    if '--access-key' in arguments:
#        i = arguments.index('--access-key')
#        access_key = arguments.pop(i+1)
#        arguments.pop(i)
#
#    # RESOURCE_SITE
#    if '--local' in arguments:
#        resource = OPTION.RESOURCE_SITE.LOCAL
#        arguments.remove('--local')
#    elif '--remote' in arguments:
#        resource = OPTION.RESOURCE_SITE.REMOTE
#        arguments.remove('--remote')
#    elif '--local-only' in arguments:
#        resource = OPTION.RESOURCE_SITE.LOCAL_ONLY
#        arguments.remove('--local-only')
#
#    # NOTE
#    if '--note' in arguments:
#        i = arguments.index('--note')
#        note = arguments.pop(i+1)
#        arguments.remove('--note')
#
#    # TARGET_TYPE
#    if '--title' in arguments:
#        target_type = OPTION.TARGET_TYPE.TITLE
#        arguments.remove('--title')
#    elif '--id' in arguments:
#        target_type = OPTION.TARGET_TYPE.IDENTIFIER
#        arguments.remove('--id')
#
#    #
#    # command
#    #
#    if len(arguments) > 0:
#        cmd = arguments.pop(0)
#    
#    #
#    # target
#    #
#    if len(arguments) > 0:
#        target = arguments[-1]
#
#    result = {
#        # cmd
#        'COMMAND':          cmd, 
#        # auth
#        'ACCESS_KEY':       access_key,
#        # options
#        'RESOURCE_SITE':    resource,
#        'NOTE':             note,
#        'FORMAT':           'xml',
#        # target
#        'TARGET_TYPE':      target_type,
#        'TARGET':           target,
#    }
#    return result
#
#
#BASE_URL = "http://api.springnote.com"
#def format_url(options):
#    url = BASE_URL
#    if options['COMMAND'] == Command.FETCH:
#        url += '/pages'
#    if options['TARGET']:
#        url += '/' + options['TARGET']
#    url += '.' + options['FORMAT']
#
#    return url


def camel2sentence(camel):
    return ''.join([' %s' % letter.lower() if letter.isupper() else letter for letter in camel]).strip()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(command_dict.keys())
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

