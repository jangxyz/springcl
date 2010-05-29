#!/usr/bin/python
usage = '''
    springcl delete [OPTIONS]              RESOURCE
    springcl delete [OPTIONS] --attachment RESOURCE --parent ID
'''
options = '''
    --attachment => is_attachment[False] : delete attachment (default is page)
    --parent ID  => parent_id<int>       : parent page id (only for attachment)
'''

from springcl_commands import *
import springcl_options
import optparse

class DeleteOption(springcl_options.SpringclOption):
    @classmethod
    def _build_parser(cls):
        p = optparse.OptionParser(usage=usage)

        gl = optparse.OptionGroup(p, 'Global options')
        springcl_options.GlobalOption._build_parser(gl)
        p.add_option_group(gl)

        #

        # resource type
        p.add_option('--attachment', action="store_true", dest="is_attachment", default=False, 
                                               help='delete attachment')
        p.add_option('--parent', metavar='ID', dest="parent_id", type=int, help='id of parent page')

        return p


class DeleteCommand(SpringclCommand):
    def __init__(self, opt_list=[]):
        self.options = DeleteOption.parse(opt_list)
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        if self.options.is_attachment:  cmd = DeleteAttachmentCommand
        else:                           cmd = DeletePageCommand

        return cmd(self.options).run()


class DeletePageCommand(DeleteCommand):
    def __init__(self, options):
        self.options = options

    def request(self, sn):
        note = self.options.note
        resource_id = int(self.options.args[0])

        page = springnote.Page(sn, id=resource_id, note=note)
        return page.delete()

    def run(self):
        result = self.try_fetch(self.request, self.options)
        self.write(self.format(result.raw), self.options.output)

        return result


class DeleteAttachmentCommand(DeleteCommand):
    def __init__(self, options):
        self.options = options
        if self.options.parent_id is None:
            raise optparse.OptionValueError("requires parent id")

    def request(self, sn):
        note, parent_id = self.options.note, self.options.parent_id
        resource_id = int(self.options.args[0])

        parent = springnote.Page(sn, id=parent_id, note=note)
        attach = springnote.Attachment(parent, id=resource_id)

        return attach.delete()

    def run(self):
        result = self.try_fetch(self.request, self.options)
        self.write(self.format(result.raw), self.options.output)

        return result

