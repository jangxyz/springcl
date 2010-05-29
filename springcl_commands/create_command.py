#!/usr/bin/python
usage = '''
    springcl create [OPTIONS] --fie FILE
    springcl create [OPTIONS] --attachment --parent ID --file FILE
'''
options = '''
    --file FILE                          : resource file
    --parent ID  => parent_id<int>       : parent page id
    --attachment => is_attachment[False] : create attachment (default is page)
'''

from springcl_commands import *
import springcl_options
import optparse

class CreateOption(springcl_options.SpringclOption):
    @classmethod
    def _build_parser(cls):
        p = optparse.OptionParser(usage=usage)

        gl = optparse.OptionGroup(p, 'Global options')
        springcl_options.GlobalOption._build_parser(gl)
        p.add_option_group(gl)

        #

        p.add_option('--file', metavar='FILE', help='file to create')
        p.add_option('--parent', metavar='ID', dest="parent_id", type=int, help='id of parent page')

        # resource type
        p.add_option('--attachment', action="store_true", dest="is_attachment", default=False, 
                                                help='create attachment')

        return p


class CreateCommand(SpringclCommand):
    def __init__(self, opt_list=[]):
        self.options = CreateOption.parse(opt_list)
        if self.options.file is None:
            raise optparse.OptionValueError("should give file to create")

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        if self.options.is_attachment:  cmd = CreateAttachmentCommand
        else:                           cmd = CreatePageCommand

        return cmd(self.options).run()


class CreatePageCommand(CreateCommand):
    def __init__(self, options):
        self.options = options

    def request(self, sn):
        note, file, parent_id = self.options.note, self.options.file, self.options.parent_id

        f = open(file)
        content = f.read()
        f.close()

        page = springnote.Page.from_json(content, sn)
        page.id   = None
        page.note = note
        page.relation_is_part_of = int(parent_id) if parent_id else None

        # save!
        return page.save()

    def run(self):
        result = self.try_fetch(self.request, self.options)
        self.write(self.format(result.raw), self.options.output)

        return result


class CreateAttachmentCommand(CreateCommand):
    def __init__(self, options):
        self.options = options
        if self.options.parent_id is None:
            raise optparse.OptionValueError("requires parent id")

    def request(self, sn):
        note, file, parent_id = self.options.note, self.options.file, self.options.parent_id

        parent = springnote.Page(sn, id=parent_id, note=note)
        attach = springnote.Attachment(parent, file=open(file))

        return attach.upload()

    def run(self):

        result = self.try_fetch(self.request, self.options)
        self.write(self.format(result.raw), self.options.output)

        return result

