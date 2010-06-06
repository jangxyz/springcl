#!/usr/bin/python

from springcl_commands import *
import simple_options

class DeleteCommand(SpringclCommand):
    usage = '''
        springcl delete [OPTIONS]              RESOURCE
        springcl delete [OPTIONS] --attachment RESOURCE --parent ID
    '''
    options = '''
        --attachment => is_attachment[False] : delete attachment (default is page)
        --parent ID  => parent_id<int>       : parent page id (only for attachment)

        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = simple_options.parser(self.usage, self.options, opt_list)
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        if self.options.is_attachment:  cmd = DeleteAttachmentCommand
        else:                           cmd = DeletePageCommand

        return cmd(self.options).run()



class DeletePageCommand(SpringclCommand):
    usage = '''
        springcl delete-page [OPTIONS] RESOURCE
    '''
    options = '''
        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = simple_options.parse(self.usage, self.options, opt_list)
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

    def request(self, sn):
        note = self.options.note
        resource_id = int(self.options.args[0])

        page = springnote.Page(sn, id=resource_id, note=note)
        return page.delete()

    def run(self):
        result = self.try_fetch(self.request, self.options)
        self.write(self.format(result.raw), self.options.output)

        return result



class DeleteAttachmentCommand(SpringclCommand):
    usage = '''
        springcl delete_attachment [OPTIONS] --attachment RESOURCE --parent ID
    '''
    options = '''
        --attachment => is_attachment[False] : delete attachment (default is page)
        --parent ID  => parent_id<int>       : parent page id (only for attachment)

        [Global Options]
    '''

    def __init__(self, opt_list=[]):
        self.options = simple_options.parse(self.usage, self.options, opt_list)
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')
        if self.options.parent_id is None:
            raise Errors.OptionError("requires parent id")

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

