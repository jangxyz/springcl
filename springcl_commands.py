from optparse import OptionParser
import springnote

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
import springcl

class SpringclCommand:
    sn_remote = springcl.make_sn()
    sn_local  = springcl.make_sn(local=True)

class ReadCommand(SpringclCommand):
    ''' read resource, either from local file system or springnote.com.

    a resource may be a page, attachment, comments, or the path where resource exist.

    usage: 
     * springcl read [--note NOTE] [--title/--id] RESOURCE
     * springcl read --comment [--note NOTE] [--title/--id] RESOURCE
     * springcl read --path [--note NOTE] [--title/--id] RESOURCE
    '''
    def __init__(self, opt_str=''):
        self.options = self.parse(opt_str)

    @classmethod
    def build_parser(cls):
        parser = OptionParser()
        parser.add_option('--note', metavar='NOTE')
        # resource pointer type
        parser.add_option('--title', action="store_true", dest="is_title", default=False)
        parser.add_option('--id',    action="store_true", dest="is_id",    default=False)


        parser.add_option('--format')

        # 
        parser.add_option('--rev', metavar='ID')
        # resource type
        parser.add_option('--comment', action="store_true", dest="is_comment")
        parser.add_option('--path',    action="store_true", dest="is_path")
        #parser.add_option('--page', metavar='PAGE_ID', action=)

        # local/remote
        parser.add_option('--local',  action="store_true", dest="run_local", help="always fetch resource locally")
        parser.add_option('--remote', action="store_true", dest="run_remote", help="always fetch resource remotely")
        parser.add_option('--remote-local', action="store_true", dest="run_local_on_fail", default=False, help="use local cache only if fetching from remote fails")

        # auth
        parser.add_option('--auth',     metavar="TOKEN")
        parser.add_option('--consumer', metavar="TOKEN")

        parser.add_option('--basedir', metavar="PATH")

        return parser

    def parse(self, opt_list):
        options, args = self.build_parser().parse_args(opt_list)

        options.args = args
        # handle run_local/run_remote/run_local_on_fail
        if options.run_remote:  options.run_local  = False 
        if options.run_local:   options.run_remote = False 
        if options.run_local_on_fail:   
            options.run_local  = False 
            options.run_remote = True

        return options

    def sn(self, option):
        return self.sn_remote if option.run_remote else self.sn_local

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
                    raise springcl.OptionError("%s is not an id" % arg)
                options.is_title = True

        if options.is_title:
            # find single resource titled `arg`
            pages = self.sn(options).list_pages(note=options.note, title=arg)
            if   len(pages) == 0: raise springcl.NoSuchResource("no page found with title '%s'. try `list` command" % arg)
            elif len(pages) >  1: raise springcl.DuplicateResources("more than one pages found with title '%s'. try `list` command" % arg)
            resource_id = pages[0].id
        return resource_id

    def get_page(self, id, options, note=None):
        ''' fetch page '''
        run_command_with = lambda sn: sn.get_page(id=id, note=note)
        try:
            result = run_command_with(self.sn(options))
        except springnote.SpringnoteError.Base, e:
            if options.run_local_on_fail:
                print e, ', trying local'
                result = run_command_with(self.sn_local)
        return result

    def get_revision(self, page, rev):
        ''' fetch revision '''
        if rev:
            if rev[0] in ('-', '+'):    key = 'index'
            else:                       key = 'id'
            page = page.get_revision(**{key: rev})
        return page


    def run(self):
        opt = self.options
        # run 
        resource_id = self.find_resource_id(opt.args[0], opt)
        page = self.get_page(id=resource_id, note=opt.note, options=opt)
        if opt.rev:
            page = self.get_revision(page, opt.rev)
        return page
            

    def format(self, **options):
        pass


