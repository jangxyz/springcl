#!/usr/bin/python
from springcl_commands import *
import simple_options

class UpdateCommand(SpringclCommand):
    usage = '''
        springcl update [OPTIONS]              RESOURCE --file FILE
        springcl update [OPTIONS] --attachment RESOURCE --file FILE --parent ID
    '''
    options = '''
        --file FILE                          : resource file
        --attachment => is_attachment[False] : update attachment (default is page)
        --parent ID  => parent_id<int>       : parent page id (only for attachment)
        
        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = simple_options.parse(self.usage, self.options, opt_list)
        if self.options.file is None:
            raise Errors.OptionError("should give file to update")
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        if self.options.is_attachment:  cmd = UpdateAttachmentCommand
        else:                           cmd = UpdatePageCommand

        return cmd(self.options).run()


class UpdatePageCommand(SpringclCommand):
    usage = 'springcl update-page [OPTIONS] RESOURCE'
    options = '''
        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = simple_options.parse(self.usage, self.options, opt_list)
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

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



class UpdateAttachmentCommand(SpringclCommand):
    usage = 'springcl update-attachment [OPTIONS] RESOURCE --file FILE --parent ID'
    options = '''
        --file FILE                         : resource file
        --parent ID => parent_id<int>       : parent page id (only for attachment)
        
        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = simple_options.parse(self.usage, self.options, opt_list)
        if self.options.file is None:
            raise Errors.OptionError("should give file to update")
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')

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

