import springnote
import filesystem_service

import optparse, sys, os

CONSUMER_TOKEN  = '5aUy7Iz0Rf7RHFflaY2kNQ'
CONSUMER_SECRET = 'oOTGX5p8v0bmPa2csaprPTbrpbSmEC17Yscn88sSJg'
BASE_PATH = os.path.expanduser("~/.springcl")

class Errors:
    class Base(Exception):          pass
    class DuplicateResources(Base): pass
    class NoSuchResource(Base):     pass
    class OptionError(Base):        pass
    class ThisShouldntHappen(Base): pass

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

def make_sn(auth, consumer=None):
    consumer = consumer or (CONSUMER_TOKEN, CONSUMER_SECRET)
    sn = springnote.Springnote(consumer_token=consumer)
    if auth:
        sn.set_access_token(auth)
    return sn

class SpringclCommand:
    _sn = None
    _remote_service = springnote.HttpRequestService()
    _local_service  = filesystem_service.FileSystemService(BASE_PATH)

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
        gl.add_option('--auth',     metavar="TOKSEC", help='use TOKSEC as access token (in TOKEN:SECRET format)')
        gl.add_option('--consumer', metavar="TOKSEC", help='use TOKSEC as consumer token')

        gl.add_option('--basedir', metavar="PATH", default=BASE_PATH, dest="basedir", help='use PATH as local cache basedir')
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
        p.add_option('--comment', action="store_true", dest="is_comment", default=False, help='get comments of the page')
        p.add_option('--path',    action="store_true", dest="is_path",    default=False, help='do not print any content of file, but the path where the cache is saved in.')
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

        # auth
        if options.auth:     options.auth     = tuple(options.auth.split(':'))
        if options.consumer: options.consumer = tuple(options.consumer.split(':'))
        else:                options.consumer = (CONSUMER_TOKEN, CONSUMER_SECRET)

        return options

    def sn(self, options, service=None):
        ''' return proper sn, according to options and service given '''
        self._sn = self._sn or make_sn(options.auth, options.consumer)

        new_service = self._remote_service if options.run_remote else self._local_service
        service = service or new_service
        if isinstance(service, filesystem_service.FileSystemService) and options.basedir:
            service.base_dir = options.basedir

        # update service of sn 
        self._sn.service = service

        return self._sn

    def last_ran_service_was_remote(self):
        return isinstance(self._sn.service, springnote.HttpRequestService)

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
        ''' try fetching resource from local, remote, or both, following 
            the options set '''
        # try
        try:
            result = fetch_method(sn=self.sn(options))
            sn = None
        except filesystem_service.FileNotExist, e:
            sn = None
            if not options.run_remote_on_fail:
                raise Errors.NoSuchResource(e.message)
            sn = self.sn(options, service=self._remote_service)

        except springnote.SpringnoteError.Base, e:
            self.write('error on remote, trying local : %s' % e, options.output)
            if not options.run_local_on_fail:
                raise e
            sn = self.sn(options, service=self._local_service)

        # retry
        if sn:
            try:
                result = fetch_method(sn=sn)
            except filesystem_service.FileNotExist, e:
                raise Errors.NoSuchResource(e.message)

        # update local cache
        if self.last_ran_service_was_remote():
            self.update_local_cache(result, options)

        return result

    def connect_default_note(self, resource_note, option_note):
        ''' change default/ directory into symlink, it not already '''
        default_path = self.format_local_path(note=None, id=None)
        if os.path.islink(default_path): return 

        # should identify the default note
        if option_note is None and resource_note is not None:
            # merge
            actual_dir = self.format_local_path(note=resource_note, id=None)
            #print 'connecting', default_path, 'to', actual_dir, '...'
            filesystem_service.merge_dir(default_path, actual_dir)

            # add symlink
            prefix = os.path.commonprefix((actual_dir, default_path))
            prelen = len(prefix)
            os.symlink(actual_dir[prelen:].rstrip('/'), default_path.rstrip('/'))

    def update_local_cache(self, resource, options):
        ''' save resource to local cache '''
        # sym link default note dir to actual note if not already
        self.connect_default_note(resource.note, options.note)

        # TODO: move this into service?
        #print 'update local cache at', path
        path = self.format_resource_path(resource, run_local=True)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        f = open(path, 'w')
        f.write(resource.raw)
        f.close()


    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        if self.options.is_comment: cmd = ReadCommentsCommand(self.options)
        if self.options.is_path:    cmd = ReadPathCommand(self.options)
        else:                       cmd = ReadPageCommand(self.options)
        return cmd.run()

    def format(self, text):
        return text
    
    def write(self, text, output):
        f = sys.stdout if output is None else open(output, 'a')
        f.write(text)
        f.write("\n")
        if output:
            f.close()

    def format_resource_path(self, resource, run_local):
        run_local = run_local or self.options.run_local
        is_page = isinstance(resource, springnote.Page) 
        page_id = resource.id if is_page else resource.parent.id
        return self.format_path(resource.note, resource.id, rev=None, run_local=run_local)

    def format_local_path(self, note, id, rev=None):
        return self._local_service.build_path(id, note, revisions=rev)

    def format_path(self, note, id, rev=None, run_local=None):
        if run_local is None:
            run_local = self.options.run_local

        if run_local:
            return self.format_local_path(note, id, rev)
        else:
            # TODO: do me!
            raise NotImplementedError("cannot return path for remote resource")


class ReadPageCommand(ReadCommand):
    ''' read a single page resource '''
    def __init__(self, options):
        self.options = options

    def fetch_page_with_revision(self, sn, note, id, rev=None):
        # fetch page
        page = springnote.Page(sn, note=note, id=id).get()
        # get revision if given
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
    ''' read list of comments from a page '''
    def __init__(self, options):
        self.options = options

    def fetch_comments_in_page(self, sn, id, note):
        return springnote.Page(sn, id=id, note=opt.note).list_comments()

    def run(self):
        # run 
        resource_id = self.find_resource_id(self.options.args[0], self.options)
        note = self.options.note

        fetch_comments = lambda sn: fetch_comments_in_page(sn, resource_id, note)
        result = self.try_fetch(fetch_comments, self.options)

        # read
        self.write(self.format(result.raw), self.options.output)

        return result


class ReadPathCommand(ReadCommand):
    ''' simply return path of target resource '''
    def __init__(self, options):
        self.options = options

    def run(self):
        resource_id = self.find_resource_id(self.options.args[0], self.options)
        note = self.options.note

        # path
        result = self.format_path(note, resource_id, self.options.rev, self.options.run_local)
        self.write(result, self.options.output)

        return result

class ReadAttachmentCommand(ReadCommand):
    ''' read a single attachment from a page '''
    def __init__(self, options):
        self.options = options
    def run(self):          pass
    def format(self, text): pass
    @classmethod
    def usage(cls):         pass

