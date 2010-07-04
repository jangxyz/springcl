#!/usr/bin/python

import env
from util import *

from springcl_commands import SpringclCommand
from read_page_command import ReadPageCommand
from read_attachment_command import ReadAttachmentCommand

class ReadCommand(SpringclCommand):
    usage = '''
        springcl read [OPTIONS] RESOURCE
        springcl read [OPTIONS] RESOURCE --parent ID 
        springcl read [OPTIONS] RESOURCE --parent ID --download
    ''' 
    options = '''
        --rev    ID<int>              : revision of page. plain number is exact identifier and numbers starting with + or - is the index
        --parent ID => parent_id<int> : parent page id (only for attachment)
        --download  => is_file[False] : content of attachment

        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = self.parse(opt_list)
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        options = self.options
        if options.parent_id: cmd = ReadAttachmentCommand
        else:                 cmd = ReadPageCommand

        return cmd(options=options).run()

