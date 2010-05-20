#!/usr/bin/python

import springnote, filesystem_service
import springcl_commands
import sys

#
# springnote constants
#
BASE_URL = "http://api.springnote.com"

commands = {
    'read': springcl_commands.ReadCommand,
}


#
# springcl constants
#
class Command:
    FETCH, COMMIT = 'fetch', 'commit'
class OPTION:
    class RESOURCE_SITE:
        LOCAL, REMOTE, LOCAL_ONLY = 'local', 'remote', 'local-only'
    class TARGET_TYPE:
        TITLE, IDENTIFIER = 'title', 'identifier'

def parse(arguments):
    cmd         = None
    access_key  = None
    resource    = None
    note        = None
    target_type = None
    target      = None

    #
    # options
    #

    # AUTHORIZATION
    if '--access-key' in arguments:
        i = arguments.index('--access-key')
        access_key = arguments.pop(i+1)
        arguments.pop(i)

    # RESOURCE_SITE
    if '--local' in arguments:
        resource = OPTION.RESOURCE_SITE.LOCAL
        arguments.remove('--local')
    elif '--remote' in arguments:
        resource = OPTION.RESOURCE_SITE.REMOTE
        arguments.remove('--remote')
    elif '--local-only' in arguments:
        resource = OPTION.RESOURCE_SITE.LOCAL_ONLY
        arguments.remove('--local-only')

    # NOTE
    if '--note' in arguments:
        i = arguments.index('--note')
        note = arguments.pop(i+1)
        arguments.remove('--note')

    # TARGET_TYPE
    if '--title' in arguments:
        target_type = OPTION.TARGET_TYPE.TITLE
        arguments.remove('--title')
    elif '--id' in arguments:
        target_type = OPTION.TARGET_TYPE.IDENTIFIER
        arguments.remove('--id')

    #
    # command
    #
    if len(arguments) > 0:
        cmd = arguments.pop(0)
    
    #
    # target
    #
    if len(arguments) > 0:
        target = arguments[-1]

    result = {
        # cmd
        'COMMAND':          cmd, 
        # auth
        'ACCESS_KEY':       access_key,
        # options
        'RESOURCE_SITE':    resource,
        'NOTE':             note,
        'FORMAT':           'xml',
        # target
        'TARGET_TYPE':      target_type,
        'TARGET':           target,
    }
    return result


def format_url(options):
    url = BASE_URL
    if options['COMMAND'] == Command.FETCH:
        url += '/pages'
    if options['TARGET']:
        url += '/' + options['TARGET']
    url += '.' + options['FORMAT']

    return url


if __name__ == '__main__':
    arg = sys.argv[1]
    cmd = commands.get(sys.argv[1], None)
    if cmd is not None:
        try:
            cmd(sys.argv[2:]).run()
        except springcl_commands.Errors.OptionError:
            print cmd.usage()
        except springcl_commands.Errors.Base, e:
            print e.__class__.__name__ + ':', e.message
            sys.exit(-1)


