#!/usr/bin/python
usage = '''
    springcl create [OPTIONS] 
    springcl create [OPTIONS] --attachment
'''
options = '''
    --file FILE                         : resource file
    --parent ID  => parent_id<int>      : parent page id
    --attachment => is_attachment<bool> : create attachment (default is page)
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
        p.add_option('--note', metavar='NOTE', help='specify note name to create resource on')

        p.add_option('--file', metavar='FILE', help='file to create')
        p.add_option('--parent', metavar='ID', dest="parent_id", type=int, help='id of parent page')

        #"--parent ID => parent_id  : id of parent page"

        # resource type
        p.add_option('--attachment', action="store_true", dest="is_attachments", default=False, help='get attachments of the page')

        return p

class CreateCommand(SpringclCommand):
    def __init__(self, opt_list=[]):
        self.options = CreateOption.parse(opt_list)

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        options = self.options
        assert options.file, "should have file to create"

        if options.is_attachments: cmd = CreateAttachmentCommand(options)
        else:                      cmd = CreatePageCommand(options)

        return cmd.run()


class CreatePageCommand(CreateCommand):
    def __init__(self, options):
        self.options = options

    def request(self, sn):
        note, file, parent_id = options.note, options.file, options.parent_id

        f = open(file)
        content = f.read()
        f.close()

        page    = springnote.Page.from_json(content, sn, note=note)
        page.id = None
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

    def request(self, sn):
        note, file, parent_id = self.options.note, self.options.file, self.options.parent_id

        parent = springnote.Page(sn, id=parent_id, note=note)
        attach = springnote.Attachment(parent, file=open(file))

        return attach.upload()

    def run(self):
        assert self.options.parent_id

        result = self.try_fetch(self.request, self.options)
        self.write(self.format(result.raw), self.options.output)

        return result

