#!/usr/bin/python
from __future__ import with_statement

import env
from util import *
from springcl_commands import SpringclCommand
import fs

import springnote

logger = get_logger(__file__)

class CreateCommand(SpringclCommand):
    usage = '''
        springcl create [OPTIONS] --file FILE
        springcl create [OPTIONS] --attachment --parent ID --file FILE
    '''
    options = '''
        --file FILE                          : resource file
        --parent ID  => parent_id<int>       : parent page id
        --attachment => is_attachment[False] : create attachment (default is page)
        
        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = self.parse(opt_list)
        if self.options.file is None:
            raise optparse.OptionValueError("should give file to create")

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        if self.options.is_attachment:  cmd = CreateAttachmentCommand
        else:                           cmd = CreatePageCommand
        return cmd(options=self.options).run()


class CreatePageCommand(SpringclCommand):
    usage = '''
        springcl create-page [OPTIONS] --file FILE
    '''
    options = '''
        --file FILE                     : resource file
        --parent ID  => parent_id<int>  : parent page id. default to root
        
        [Global Options]
    '''
    def __init__(self, opt_list=[], options=None):
        if options: self.options = options
        else:       self.options = self.parse(opt_list)
        if self.options.file is None:
            raise Exception("should give file to create")

    def request(self, sn):
        parent_id = self.options.parent_id
        content   = fs.read_file(self.options.file)

        # set page
        page = springnote.Page.from_json(content, sn)
        page.id   = None
        page.note = self.options.note
        page.relation_is_part_of = int(parent_id) if parent_id else None
        # save!
        return page.save(verbose=None)

    def run(self):
        result = self.try_fetch(self.request)
        self.write(self.format(result.raw), self.options.output)

        return result


class CreateAttachmentCommand(SpringclCommand):
    usage = '''
        springcl create-attachment [OPTIONS] --parent ID --file FILE
    '''
    options = '''
        --file FILE                          : resource file
        --parent ID  => parent_id<int>       : parent page id
        
        [Global Options]
    '''
    def __init__(self, opt_list=[], options=None):
        if options:
            self.options = options
        else:
            self.options = self.parse(opt_list)
            if self.options.file is None:
                raise optparse.OptionValueError("should give file to create")

    def request(self, sn):
        options = self.options

        parent = springnote.Page(sn, id=options.parent_id, note=options.note)
        attach = springnote.Attachment(parent, file=open(options.file))

        return attach.upload()

    def run(self):
        result = self.try_fetch(self.request, self.options)
        self.write(self.format(result.raw), self.options.output)
        return result


