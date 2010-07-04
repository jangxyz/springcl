#!/usr/bin/python

import env
from util import *
import simple_options
from springcl_commands import *

class ReadPageCommand(SpringclCommand):
    usage = '''
        springcl read-page [OPTIONS] RESOURCE
        springcl read-page [OPTIONS] RESOURCE --rev ID
    '''
    options = '''
        --rev ID<int> : revision of page. plain number is exact identifier and numbers starting with + or - is the index

        # output
        --format STR   : print output in format string
        --attribute STR : print only attribute

        [Global Options]
    '''
    def __init__(self, opt_list=[], options=None):
        self.options = self.parse(opt_list) if options is None else options

    def fetch(self, sn, note, id, rev=None):
        page = springnote.Page(sn, note=note, id=id).get()
        if rev:
            if rev[0] in ('-', '+'):    key = 'index'
            else:                       key = 'id'
            page = page.get_revision(**{key: int(rev)})
        return page

    def run(self):
        ''' fetch a page with specific id, note and revision, with options '''
        options = self.options

        # fetch
        page_id = int(options.args[0])
        note    = options.note or options.default_note
        fetch_page = lambda sn: self.fetch(sn, note, page_id, options.rev)
        result  = self.try_fetch(fetch_page)

        # write 
        if self.fetched_from_remote: 
            self.update_cache(result)

        self.write(self.format(result.raw), options.output)

        return result

    def format_raw(self, text=None, resource=None):
        ''' pretty print default json '''
        assert text or resource, "either text or resource must be set"
        
        if resource is None:
            import springnote, types
            resource = springnote.json.loads(text)

        def page_resource_order(x):
            orders = _w('''
            	identifier title tags uri
            	date_created date_modified rights version
            	relation_is_part_of
            	creator contributor_modified
            	source
            ''')
            if x not in orders:
                return -1
            return orders.index(x)

        def format_dict(resource, depth=0, file=None):
            from cStringIO import StringIO
            file = file or StringIO()

            tab0 = 4 * (depth  ) * ' '
            tab1 = 4 * (depth+1) * ' '

            file.write('{' + "\n")
            sorted_keys = sorted(resource.keys(), key=page_resource_order)
            for key in sorted_keys:
                file.write(tab1 + '"%(key)s": ' % locals())
                value = resource[key]
                if isinstance(value, types.DictType):
                    value = format_dict(value, depth+1).getvalue()
                else:
                    value = springnote.json.dumps(value)
                file.write(value)
                if key != sorted_keys[-1]: 
                    file.write(',')
                file.write("\n")
            file.write(tab0 + '}')
            return file
        return format_dict(resource).getvalue()

    def format_attribute(self, resource, attribute):
        assert attribute in springnote.Page.springnote_attributes
        return resource['page'][attribute].encode('utf-8')

    def format_string(self, resource, format_str):
        return (format_str % resource['page']).encode('utf-8')

    def format(self, text):
        resource = springnote.json.loads(text)

        if self.options.format:
            return self.format_string(resource, self.options.format)
        if self.options.attribute:
            return self.format_attribute(resource, self.options.attribute)
        else:
            return self.format_raw(text)

    def update_cache(self, page):
        assert self.options.basedir is not None, 'needs base dir!'

        import filesystem_service
        local_service = filesystem_service.FileSystemService(self.options.basedir)
        path = local_service.build_path(page.id, page.note)

        self.write(self.format(page.raw), path)


