#!/usr/bin/python
usage = '''
    springcl list [OPTIONS] RESOURCE
    springcl list [OPTIONS] RESOURCE --attachments
    springcl list [OPTIONS] RESOURCE --comments
    springcl list [OPTIONS] RESOURCE --revisions
    springcl list [OPTIONS] RESOURCE --pages
'''

from springcl_commands import *
import springcl_options
import optparse

class ListOption(springcl_options.SpringclOption):
    @classmethod
    def _build_parser(cls):
        p = optparse.OptionParser(usage=usage)

        gl = optparse.OptionGroup(p, 'Global options')
        springcl_options.GlobalOption._build_parser(gl)
        p.add_option_group(gl)

        #
        p.add_option('--note', metavar='NOTE', help='specify note name to read resource from')

        # resource pointer type
        #p.add_option('--title', action="store_true", dest="is_title", default=False, help='RESOURCE is page title. error if multiple pages found')
        #p.add_option('--id',    action="store_true", dest="is_id",    default=False, help='RESOURCE is page id. error if non numeric')
        #p.add_option('--format', help='specify format in action')

        # resource type
        p.add_option('--attachments', action="store_true", dest="is_attachments", default=False, help='get attachments of the page')
        p.add_option('--revisions'  , action="store_true", dest="is_revisions"  , default=False, help='get revisions of the page')
        p.add_option('--pages'      , action="store_true", dest="is_pages"      , default=False, help='get children pages of the page')
        p.add_option('--comments'   , action="store_true", dest="is_comments"   , default=False, help='get comments of the page')

        return p

class ListCommand(SpringclCommand):
    def __init__(self, opt_list=[]):
        self.options = ListOption.parse(opt_list)
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        options = self.options

        if options.is_attachments: cmd = ListAttachmentsCommand
        elif options.is_revisions: cmd = ListRevisionsCommand
        elif options.is_comments:  cmd = ListCommentsCommand
        else:                      cmd = ListPagesCommand

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


class ListPagesCommand(ListCommand):
    @classmethod
    def fetch(cls, sn, id, note):
        return springnote.Page(sn, id=id, note=note).get_children()

class ListRevisionsCommand(ListCommand):
    @classmethod
    def fetch(self, sn, page_id, note):
        return springnote.Page(sn, id=page_id, note=note).list_revisions()

class ListAttachmentsCommand(ListCommand):
    @classmethod
    def fetch(self, sn, id, note):
        return springnote.Page(sn, id=id, note=note).list_attachments()

class ListCommentsCommand(ListCommand):
    @classmethod
    def fetch(self, sn, id, note):
        return springnote.Page(sn, id=id, note=note).list_comments()

