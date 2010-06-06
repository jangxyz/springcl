#!/usr/bin/python

from springcl_commands import *
import simple_options

class ReadCommand(SpringclCommand):
    usage = '''
        springcl read [OPTIONS] RESOURCE
        springcl read [OPTIONS] RESOURCE --attachment ATTACHMENT 
        springcl read [OPTIONS] RESOURCE --attachment ATTACHMENT --file
    ''' 
    options = '''
        --rev        ID<int>     : revision of page. plain number is exact identifier and numbers starting with + or - is the index
        --attachment ID<int>     : attachment of page
        --file => is_file[False] : content of attachment

        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = simple_options.parse(self.usage, self.options, opt_list)
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        options = self.options
        if   options.attachment: cmd = ReadAttachmentCommand(options)
        else:                    cmd = ReadPageCommand(options)

        return cmd.run()


def init_command(self, opt_list, options):
    if options: 
        self.options = options
    else:
        self.options = simple_options.parse(self.usage, self.options, opt_list)
        if self.options.file is None:
            raise Errors.OptionError('needs resource argument')

class ReadPageCommand(ReadCommand):
    usage = 'springcl read [OPTIONS] RESOURCE' 
    options = '''
        --rev ID<int> : revision of page. plain number is exact identifier and numbers starting with + or - is the index

        [Global Options]
    '''
    def __init__(self, opt_list=[], options=None):
        init_command(self, opt_list, options)

    def fetch(self, sn, note, id, rev=None):
        page = springnote.Page(sn, note=note, id=id).get()
        if rev:
            if rev[0] in ('-', '+'):    key = 'index'
            else:                       key = 'id'
            page = page.get_revision(**{key: int(rev)})
        return page

    def run(self):
        ''' fetch a page with specific id, note and revision, with options '''
        options = self.options

        # fetch
        page_id = int(options.args[0])
        fetch   = lambda sn: self.fetch(sn, options.note, page_id, options.rev)
        result  = self.try_fetch(fetch_method=fetch, options=options)

        # read
        self.write(self.format(result.raw), options.output)
        return result


class ReadAttachmentCommand(ReadCommand):
    usage = '''
        springcl read [OPTIONS] RESOURCE --attachment ATTACHMENT 
        springcl read [OPTIONS] RESOURCE --attachment ATTACHMENT --file
    ''' 
    options = '''
        --attachment ID<int>     : attachment of page
        --file => is_file[False] : content of attachment

        [Global Options]
    '''
    def __init__(self, opt_list=[], options=None):
        init_command(self, opt_list, options)

    def fetch(self, sn, note, page_id, attachment_id, is_file):
        assert attachment_id

        page = springnote.Page(sn, note=note, id=page_id)
        attach = springnote.Attachment(page, id=attachment_id)
        
        if is_file: attach.download()
        else:       attach.get()
        return attach

    def run(self):
        ''' fetch an attachment with specific id, note and page_id, with options '''
        options   = self.options

        # fetch
        page_id   = int(options.args[0])
        attach_id = options.attachment
        fetch  = lambda sn: self.fetch(sn, options.note, page_id, attach_id, options.is_file)
        result = self.try_fetch(fetch_method=fetch, options=options)

        # read
        self.write(self.format(result.raw), options.output)

        return result


