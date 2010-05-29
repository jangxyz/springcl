#!/usr/bin/python

usage = '''
    springcl read [OPTIONS] RESOURCE
    springcl read [OPTIONS] RESOURCE --attachment ATTACHMENT 
    springcl read [OPTIONS] RESOURCE --attachment ATTACHMENT --file
''' 
options = '''
    --rev        ID<int>     : revision of page. plain number is exact identifier and numbers starting with + or - is the index
    --attachment ID<int>     : attachment of page
    --file => is_file[False] : content of attachment
'''

'''
Read

    read resource from springnote.com.
    a resource may be a page, a revision of a page, or attachment.

    need to know:
        * note
        * page_id
        * revision_id(x)
        * attachment_id
        * attachment_info
        * attachment_content
'''

from springcl_commands import *
import springcl_options
import optparse, sys, os

class ReadOption(springcl_options.SpringclOption):
    @classmethod
    def _build_parser(cls):
        p = optparse.OptionParser(usage=usage)

        # Global Options
        gl = optparse.OptionGroup(p, 'Global options')
        springcl_options.GlobalOption._build_parser(gl)
        p.add_option_group(gl)

        #

        # resource pointer type
        #p.add_option('--title', action="store_true", dest="is_title", default=False, help='RESOURCE is page title. error if multiple pages found')
        #p.add_option('--id',    action="store_true", dest="is_id",    default=False, help='RESOURCE is page id. error if non numeric')
        p.add_option('--rev',   metavar='ID', help='revision of page. plain number is exact identifier and numbers starting with + or - is the index')
        #p.add_option('--format', help='specify format in action')

        # resource type
        p.add_option('--attachment', metavar='ID', type=int, help='attachment of page')
        p.add_option('--file', action="store_true", dest="is_file", help='content of attachment')

        return p

class ReadCommand(SpringclCommand):
    def __init__(self, opt_list=[]):
        self.options = ReadOption.parse(opt_list)
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        options = self.options
        if   options.attachment: cmd = ReadAttachmentCommand(options)
        else:                    cmd = ReadPageCommand(options)

        return cmd.run()


class ReadPageCommand(ReadCommand):
    ''' read a single page resource '''
    def __init__(self, options):
        self.options = options

    def fetch_page_with_revision(self, sn, note, id, rev=None):
        page = springnote.Page(sn, note=note, id=id).get()
        if rev:
            if rev[0] in ('-', '+'):    key = 'index'
            else:                       key = 'id'
            page = page.get_revision(**{key: int(rev)})
        return page

    def run(self):
        ''' fetch a page with specific id, note and revision, with options '''
        options = self.options
        page_id = int(options.args[0])
        note, rev = options.note, options.rev

        # fetch
        fetch = lambda sn: self.fetch_page_with_revision(sn, note, page_id, rev)
        result = self.try_fetch(fetch_method=fetch, options=options)

        # read
        self.write(self.format(result.raw), options.output)

        return result


class ReadAttachmentCommand(ReadCommand):
    ''' read a single attachment from a page '''
    def __init__(self, options):
        self.options = options

    def fetch_attachment(self, sn, note, page_id, attachment_id, is_file):
        assert attachment_id

        page = springnote.Page(sn, note=note, id=page_id)
        attach = springnote.Attachment(page, id=attachment_id)
        
        if is_file: attach.download()
        else:       attach.get()
        return attach

    def run(self):
        ''' fetch an attachment with specific id, note and page_id, with options '''
        options   = self.options
        page_id   = int(options.args[0])
        note      = options.note
        attach_id = options.attachment

        # fetch
        fetch = lambda sn: self.fetch_attachment(sn, note, page_id, attach_id, options.is_file)
        result = self.try_fetch(fetch_method=fetch, options=options)

        # read
        self.write(self.format(result.raw), options.output)

        return result

