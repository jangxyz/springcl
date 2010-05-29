#!/usr/bin/python
from springcl_commands import *

class DeletePageCommand(SpringclCommand):
    usage = '''
        springcl delete-page [OPTIONS] RESOURCE
    '''
    def __init__(self, opt_list=[]):
        self.options = DeletePageOption.parse(opt_list)
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


import springcl_options, optparse
class DeletePageOption(springcl_options.SpringclOption):
    @classmethod
    def _build_parser(cls):
        p = optparse.OptionParser(usage=DeletePageCommand.usage)

        gl = optparse.OptionGroup(p, 'Global options')
        springcl_options.GlobalOption._build_parser(gl)
        p.add_option_group(gl)

        return p



