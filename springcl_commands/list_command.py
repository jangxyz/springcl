#!/usr/bin/python

from springcl_commands import *
import simple_options

class ListCommand(SpringclCommand):
    usage = '''
        springcl list [OPTIONS] RESOURCE
        springcl list [OPTIONS] RESOURCE --attachments
        springcl list [OPTIONS] RESOURCE --comments
        springcl list [OPTIONS] RESOURCE --revisions
        springcl list [OPTIONS] RESOURCE --pages
    '''
    options = '''
        --attachments => is_attachments[False] : get attachments of the page
        --revisions   => is_revisions  [False] : get revisions of the page
        --pages       => is_pages      [True]  : get children pages of the page
        --comments    => is_comments   [False] : get comments of the page

        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = simple_options.parse(self.usage, self.options, opt_list)
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        options = self.options

        if   options.is_attachments: cmd = ListAttachmentsCommand()
        elif options.is_revisions:   cmd = ListRevisionsCommand()
        elif options.is_comments:    cmd = ListCommentsCommand()
        else:                        cmd = ListPagesCommand()

        # run 
        page_id = int(self.options.args[0])
        note = self.options.note

        fetch   = lambda sn: cmd.fetch(sn, page_id, note)
        results = self.try_fetch(fetch, self.options)

        # read
        for result in results:
            result.raw = result.raw.encode('utf-8')
            self.write(self.format(result.raw), self.options.output)

        return results


def init_command(self, opt_list, options):
    if options: 
        self.options = options
    else:
        self.options = simple_options.parse(self.usage, self.options, opt_list)

def run_command(self):
    options = self.options

    # run 
    page_id = int(self.options.args[0])
    fetch   = lambda sn: self.fetch(sn, page_id, options.note)
    results = self.try_fetch(fetch, options)

    # read
    for result in results:
        result.raw = result.raw.encode('utf-8')
        self.write(self.format(result.raw), options.output)

    return results


class ListPagesCommand(ListCommand):
    usage   = 'springcl list-pages [OPTIONS] RESOURCE'
    options = '''
        [Global Options]
    '''
    def __init__(self, opt_list=[], options=None): 
        init_command(self, opt_list, options)
    def run(self): 
        return run_command(self)

    def fetch(cls, sn, id, note):
        return springnote.Page(sn, id=id, note=note).get_children()


class ListRevisionsCommand(ListCommand):
    usage   = 'springcl list-revisions [OPTIONS] RESOURCE'
    options = '''
        [Global Options]
    '''
    def __init__(self, opt_list=[], options=None): 
        init_command(self, opt_list, options)
    def run(self): 
        return run_command(self)

    def fetch(self, sn, page_id, note):
        return springnote.Page(sn, id=page_id, note=note).list_revisions()

class ListAttachmentsCommand(ListCommand):
    usage   = 'springcl list-attachments [OPTIONS] RESOURCE'
    options = '''
        [Global Options]
    '''
    def __init__(self, opt_list=[], options=None): 
        init_command(self, opt_list, options)
    def run(self): 
        return run_command(self)
    
    def fetch(self, sn, id, note):
        return springnote.Page(sn, id=id, note=note).list_attachments()

class ListCommentsCommand(ListCommand):
    usage   = 'springcl list-comments [OPTIONS] RESOURCE'
    options = '''
        [Global Options]
    '''
    def __init__(self, opt_list=[], options=None): 
        init_command(self, opt_list, options)
    def run(self): 
        return run_command(self)

    def fetch(self, sn, id, note):
        return springnote.Page(sn, id=id, note=note).list_comments()


