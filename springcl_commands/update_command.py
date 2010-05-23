#!/usr/bin/python
usage = '''
    springcl update [OPTIONS] RESOURCE --file FILE
    springcl update [OPTIONS] RESOURCE --attachment --file FILE
'''
options = '''
    --file FILE                          : resource file
    --attachment => is_attachment[False] : update attachment (default is page)
    --parent ID  => parent_id<int>       : parent page id (only for attachment)
'''

from springcl_commands import *
import springcl_options
import optparse


class UpdateOption(springcl_options.SpringclOption):
    @classmethod
    def _build_parser(cls):
        p = optparse.OptionParser(usage=usage)

        gl = optparse.OptionGroup(p, 'Global options')
        springcl_options.GlobalOption._build_parser(gl)
        p.add_option_group(gl)

        #
        p.add_option('--note', metavar='NOTE', help='specify note name to update resource on')
        p.add_option('--file', metavar='FILE', help='resource file to update with')

        # resource type
        p.add_option('--attachment', action="store_true", dest="is_attachment", default=False, 
                                               help='update attachment')
        p.add_option('--parent', metavar='ID', dest="parent_id", type=int, help='id of parent page')

        return p


class UpdateCommand(SpringclCommand):
    def __init__(self, opt_list=[]):
        self.options = UpdateOption.parse(opt_list)
        if self.options.file is None:
            raise Errors.OptionError("should give file to update")
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        if self.options.is_attachment:  cmd = UpdateAttachmentCommand
        else:                           cmd = UpdatePageCommand

        return cmd(self.options).run()


class UpdatePageCommand(UpdateCommand):
    def __init__(self, options):
        self.options = options

    def request(self, sn):
        note = self.options.note
        file = self.options.file
        resource_id = int(self.options.args[0])

        f = open(file)
        content = f.read()
        f.close()

        page = springnote.Page.from_json(content, auth=sn)
        page.note = note
        if page.id and page.id != resource_id:
            raise springcl_commands.OptionError("identifier is %d in %s" % (page.id, file))
        page.id = resource_id

        # save!
        return page.save()

    def run(self):
        result = self.try_fetch(self.request, self.options)
        self.write(self.format(result.raw), self.options.output)

        return result


class UpdateAttachmentCommand(UpdateCommand):
    def __init__(self, options):
        self.options = options
        if self.options.parent_id is None:
            raise optparse.OptionValueError("requires parent id")

    def request(self, sn):
        note, file, parent_id = self.options.note, self.options.file, self.options.parent_id
        resource_id = int(self.options.args[0])

        parent = springnote.Page(sn, id=parent_id, note=note)
        attach = springnote.Attachment(parent, file=open(file))
        attach.id = resource_id

        return attach.upload()

    def run(self):
        result = self.try_fetch(self.request, self.options)
        self.write(self.format(result.raw), self.options.output)

        return result

