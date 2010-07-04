#!/usr/bin/python

import env
from util import *
from springcl_commands import SpringclCommand

class ReadAttachmentCommand(SpringclCommand):
    usage = '''
        springcl read-attachment [OPTIONS] RESOURCE --parent ID
        springcl read-attachment [OPTIONS] RESOURCE --parent ID --download
    ''' 
    options = '''
        --parent ID => parent_id<int> : parent page id
        --download  => is_file[False] : content of attachment

        [Global Options]
    '''
    def __init__(self, opt_list=[], options=None):
        if options: self.options = options
        else:       self.options = self.parse(opt_list)

    def fetch(self, sn, note, page_id, attachment_id, is_file):
        assert attachment_id

        page = springnote.Page(sn, note=note, id=page_id)
        attach = springnote.Attachment(page, id=attachment_id)
        
        if is_file: attach.download()
        else:       attach.get()
        return attach

    def run(self):
        ''' fetch an attachment with specific id, note and page_id, with options '''
        options = self.options

        # fetch
        page_id   = options.parent_id
        attach_id = int(options.args[0])

        fetch  = lambda sn: self.fetch(sn, options.note, page_id, attach_id, options.is_file)
        result = self.try_fetch(fetch_method=fetch, options=options)

        # read
        self.write(self.format(result.raw), options.output)

        return result

