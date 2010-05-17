import springnote
import filesystem_service

import optparse, sys

class Errors:
    class DuplicateResources(Exception): pass
    class NoSuchResource(Exception)    : pass
    class OptionError(Exception)       : pass

## dep.
class Option:
    def __init__(self, **options):
        for key,value in options.iteritems():
            setattr(self, key, value)

    @staticmethod
    def build_parser():
        pass

class ReadOption(Option):
    COMMENTS, PAGE, ATTACHMENT, PATH = range(4)
    command = None
    target_resource = None # (Comments, Page, Attachment)
    path    = None
    format  = None

class ResourcePointer:
    ''' container holding information to point resource '''
    def __init__(self, **kwarg):
        self.note = kwarg.get('note')
        self.id   = kwarg.get('id')
        # page (revision)
        self.rev       = None
        self.rev_index = None
        self.rev, self.rev_index = self.set_rev(kwarg.get('rev'))

        # attachment
        self.parent_id = kwarg.get('page')

        # comment
        is_comment = kwarg.get('comment')

        # class of resource
        self.typed(is_comment)

    def typed(self, is_comment=False):
        if self.parent_id:  self.type = springnote.Attachment
        elif is_comment:    self.type = springnote.Comment
        else:               self.type = springnote.Page
        return self

    def set_rev(self, value):
        rev, rev_index = None, None
        if value:
            if any(map(value.startswith, ['-', '+'])):
                rev_index = int(value)
            else:
                rev = int(value)
        return rev, rev_index

    def get_parent(self):
        if self.parent_id:
            return ResourcePointer(note=self.note, id=self.parent_id)


#class LocalSpringnote(springnote.Springnote):
#    def __init__(self, access_token=None, consumer_token=(DEFAULT_CONSUMER_TOKEN_KEY, DEFAULT_CONSUMER_TOKEN_SECRET), verbose=None):
#        pass
#
#    def springnote_request(self, method, url, params={}, headers=None, body=None, 
#            sign_token=None, secure=False, verbose=False):
#        pass
#
#    def parse_url(self, url):
#        ''' return resource pointer '''
#        path = urllib.splithost(urllib.splittype(url)[-1])[-1]
#        path, query = urllib.splitquery(path)
#
#        rp = ResourcePointer()
#        for field, value in map(urllib.splitvalue, query.split('&')):
#            if 'domain' == field: rp.note = value
#
#        remain = path
#        dummy, sep, remain = remain.partition('/pages')
#        # /pages.json => list of pages
#        if remain.starswith('.'): return rp.typed()
#
#        # page id
#        remain = remain.lstrip('/')
#        id, sep, remain = remain.partition('/')
#        rp.id = int(id)
#
#        # /pages/123.json => single page
#        if remain.startswith('.'): return rp.typed()
#
#        # attachment
#        if remain.startswith('attachments'):
#            rp.parent_id = rp.id
#            if   remain.startswith('attachments.'):
#                rp.id = None
#            elif remain.startswith('attachments/'):
#                id, sep, remain = remain.partition('.')
#                rp.id = int(id)
#            return rp.typed()
#
#        elif remain.startswith('revisions'):
#            pass
#
#
#
#
#
#
#
#class Format:
#    def convert(self, resource):
#        return resource.raw
#
#class ReadCommand:
#    def __init__(self, options):
#        self.options = options
#
#    def run(self):
#        options = self.options
#        if   self.PAGE       == options.command: return self.read_page()
#        elif self.ATTACHMENT == options.command: return self.read_attachment()
#        elif self.COMMENTS   == options.command: return self.read_comments()
#        elif self.PATH       == options.command: return self.read_path()
#        else:
#            raise InvalidOption("does not know command: %s" % options.command)
#
#    def read_page(self):
#        page = sn.get_page(options.resource)
#        return options.format.convert(page)
#
#    def read_attachment(self):
#        page   = sn.get_page(options.resource.get_parent())
#        attach = page.get_attachment(options.resource)
#        return options.format.convert(attach)
#
#    def read_comments(self):
#        page     = sn.get_page(options.resource)
#        comments = page.get_comments()
#        return options.format.convert(comments)
#
#    def read_path(self):
#        return self.make_path(self.options)
#
#    @classmethod
#    def make_path(self, options):
#        path = os.path.join(options.base_dir, options.note, options.page_id)
#        if options.format is None:
#            return os.path.join(path, options.page_id + ".xhtml")


#class GlobalOption(Option):
#    local 
#    remote 
#    both (local-then-remote) 
#    auth ARG 
#    format FORMAT 


#
# springcl commands
#

def make_sn(service=None):
    return springnote.Springnote(service=service)

class SpringclCommand:
    _sn = None
    _remote_service = springnote.HttpRequestService()
    _local_service  = filesystem_service.FileSystemService()

class ReadCommand(SpringclCommand):
    ''' read resource, either from local file system or springnote.com.

    a resource may be a page, attachment, comments, or the path where resource exist.

    usage: 
     * springcl read [--note NOTE] [--title/--id] RESOURCE
     * springcl read --comment [--note NOTE] [--title/--id] RESOURCE
     * springcl read --path [--note NOTE] [--title/--id] RESOURCE
    '''
    def __init__(self, opt_list=''):
        self.options = self.parse(opt_list)
        if len(self.options.args) is 0:
            raise Errors.OptionError('needs resource argument')
    
    @classmethod
    def usage(cls):
        return cls.build_parser().usage

    @classmethod
    def build_parser(cls):
        p = optparse.OptionParser(usage=
            'usage: springcl read [OPTIONS] RESOURCE\n'                       \
            '       springcl read [OPTIONS] RESOURCE --comment\n'             \
            '       springcl read [OPTIONS] RESOURCE --page PAGE_RESOURCE\n'  \
            '       springcl read [OPTIONS] RESOURCE --path'
        )

        #
        # Global Options
        #
        gl = optparse.OptionGroup(p, 'Global options')

        # local/remote
        gl.add_option('--local',  action="store_true", dest="run_remote_on_fail", default=False, help="local first, remote only when failed")
        gl.add_option('--remote', action="store_true", dest="run_local_on_fail",  default=False, help="remote first, local only when failed")
        gl.add_option('--local-only',  action="store_true", dest="run_local",  default=False, help="always fetch resource locally")
        gl.add_option('--remote-only', action="store_true", dest="run_remote", default=False, help="always fetch resource remotely")

        # auth
        gl.add_option('--auth',     metavar="TOKKEY", help='use TOKKEY as access token (TOKKEY is TOKEN:KEY format)')
        gl.add_option('--consumer', metavar="TOKKEY", help='use TOKKEY as consumer token')

        gl.add_option('--basedir', metavar="PATH", dest="basedir", help='use PATH as local cache basedir')
        gl.add_option('--output', metavar="FILE", default=None, help='output file')
        p.add_option_group(gl)

        #
        #
        #

        p.add_option('--note', metavar='NOTE', help='specify note name to read resource from')

        # resource pointer type
        p.add_option('--title', action="store_true", dest="is_title", default=False, help='RESOURCE is page title. error if multiple pages found')
        p.add_option('--id',    action="store_true", dest="is_id",    default=False, help='RESOURCE is page id. error if non numeric')
        p.add_option('--rev',   metavar='ID', help='revision of page. plain number is exact identifier and numbers starting with + or - is the index')
        p.add_option('--format', help='specify format in action')

        # resource type
        p.add_option('--comment', action="store_true", dest="is_comment", help='get comments of the page')
        p.add_option('--path',    action="store_true", dest="is_path", help='do not print any content of file, but the path where the cache is saved in.')
        #p.add_option('--page', metavar='PAGE_ID', action=)

        return p

    def parse(self, opt_list):
        options, args = self.build_parser().parse_args(opt_list)

        options.args = args
        # handle run_local/run_remote/run_local_on_fail/run_remote_on_fail
        if   options.run_remote_on_fail: options.run_local  = True # local
        elif options.run_local_on_fail:  options.run_remote = True # remote
        elif options.run_remote:         pass                      # remote-only
        elif options.run_local:          pass                      # local-only

        return options

    def sn(self, option, service=None):
        self._sn = self._sn or make_sn()

        new_service = self._remote_service if option.run_remote else self._local_service
        service = service or new_service

        if isinstance(service, filesystem_service.FileSystemService) and option.basedir:
            service.base_dir = option.basedir

        # update service of sn 
        self._sn.service = service

        return self._sn

    def find_resource_id(self, arg, options):
        ''' find resource id from given arg and options 

        * options.is_id   : arg is resource id (should be int)
        * options.is_title: arg is title, so list pages and find out the id of 
                            the titled page (error if none or more than one)
        * neither         : id if numeric, title if not
        '''
        if not options.is_title:
            # try parsing it as id first
            try:
                resource_id = int(arg)
            except ValueError:
                if options.is_id:
                    raise Errors.OptionError("%s is not an id" % arg)
                options.is_title = True

        if options.is_title:
            # find single resource titled `arg`
            sn    = self.sn(options)
            pages = springnote.Page.list(sn, note=options.note, title=arg)
            if   len(pages) == 0: raise Errors.NoSuchResource("no page found with title '%s'. try `list` command" % arg)
            elif len(pages) >  1: raise Errors.DuplicateResources("more than one pages found with title '%s'. try `list` command" % arg)
            resource_id = pages[0].id
        return resource_id

    def try_fetch(self, fetch_method, options):
        ''' try fetching resource from local, remote, or both, following the options '''
        # try
        try:
            result = fetch_method(sn=self.sn(options))
            sn = None
        except filesystem_service.FileNotExist, e:
            sn = None
            if options.run_remote_on_fail:
                sn = self.sn(options, service=self._remote_service)
            else:
                raise e
        except springnote.SpringnoteError.NoNetwork, e:
            if options.run_local_on_fail:
                sn = self.sn(options, service=self._local_service)
            else:
                raise e
        # retry
        if sn:
            result = fetch_method(sn=sn)
        return result

    def run_list_comments(self, id, note=None, options=None):
        ''' fetch comments of the page '''
        fetch_page_comments = lambda sn: springnote.Page(sn, id=id, note=note).list_comments()
        return self.try_fetch(fetch_page_comments, options)

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        #opt = self.options
        ## run 
        #resource_id = self.find_resource_id(opt.args[0], opt)
        #if opt.is_comment:
        #    result = self.run_list_comments(id=resource_id, note=opt.note, options=opt)
        #else:
        #    result = self.run_get_page(id=resource_id, note=opt.note, rev=opt.rev, options=opt)
        #print self.format(result.raw)
        #return result
        if self.options.is_comment:
            cmd = ReadCommentsCommand(self)
        else:
            cmd = ReadPageCommand(self)

        return cmd.run()

    def format(self, text):
        return text
    
    def write(self, text, output):
        f = sys.stdout if output is None else open(output, 'a')
        f.write(text)
        if output:
            f.close()


class ReadPageCommand(ReadCommand):
    ''' read a single page resource '''
    def __init__(self, read):
        self.parent  = read
        self.options = self.parent.options

    def fetch_page_with_revision(self, sn, note, id, rev):
        # fetch page
        page = springnote.Page(sn, id=id, note=note).get()
        # get rev if given
        if rev:
            if rev[0] in ('-', '+'):    key = 'index'
            else:                       key = 'id'
            page = page.get_revision(**{key: rev})
        return page

    def run(self):
        ''' fetch a page with specific id, note and revision, with options '''
        options = self.options
        id = self.find_resource_id(options.args[0], options)
        note, rev = options.note, options.rev

        # fetch
        fetch_page = lambda sn: self.fetch_page_with_revision(sn, note, id, rev)
        result = self.try_fetch(fetch_method=fetch_page, options=options)

        # read
        self.write(self.format(result.raw), options.output)

        return result

class ReadCommentsCommand(ReadCommand):
    ''' read comments from a page '''
    def __init__(self, read):
        self.parent  = read
        self.options = self.parent.options

    def fetch_comments_in_page(self, sn, id, note):
        return springnote.Page(sn, id=id, note=opt.note).list_comments()

    def run(self):
        opt = self.options
        # run 
        resource_id = self.find_resource_id(opt.args[0], opt)
        note = opt.note

        fetch_comments = lambda sn: fetch_comments_in_page(sn, resource_id, note)
        result = self.try_fetch(fetch_comments, options)

        # read
        self.write(self.format(result.raw), options.output)

        return result


class ReadAttachmentCommand(ReadCommand):
    ''' read a single attachment from a page '''
    def __init__(self, options):
        self.options = options
    def run(self):          pass
    def format(self, text): pass
    @classmethod
    def usage(cls):         pass

