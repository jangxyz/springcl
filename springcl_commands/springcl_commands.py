import springnote, filesystem_service
import os, sys

CONSUMER_TOKEN  = '5aUy7Iz0Rf7RHFflaY2kNQ'
CONSUMER_SECRET = 'oOTGX5p8v0bmPa2csaprPTbrpbSmEC17Yscn88sSJg'
BASE_PATH = os.path.expanduser("~/.springcl")

class Errors:
    class Base(Exception):          pass
    class DuplicateResources(Base): pass
    class NoSuchResource(Base):     pass
    class OptionError(Base):        pass
    class ThisShouldntHappen(Base): pass

### dep.
#class Option:
#    def __init__(self, **options):
#        for key,value in options.iteritems():
#            setattr(self, key, value)
#
#    @staticmethod
#    def build_parser():
#        pass
#
#class ReadOption(Option):
#    COMMENTS, PAGE, ATTACHMENT, PATH = range(4)
#    command = None
#    target_resource = None # (Comments, Page, Attachment)
#    path    = None
#    format  = None
#
#class ResourcePointer:
#    ''' container holding information to point resource '''
#    def __init__(self, **kwarg):
#        self.note = kwarg.get('note')
#        self.id   = kwarg.get('id')
#        # page (revision)
#        self.rev       = None
#        self.rev_index = None
#        self.rev, self.rev_index = self.set_rev(kwarg.get('rev'))
#
#        # attachment
#        self.parent_id = kwarg.get('page')
#
#        # comment
#        is_comment = kwarg.get('comment')
#
#        # class of resource
#        self.typed(is_comment)
#
#    def typed(self, is_comment=False):
#        if self.parent_id:  self.type = springnote.Attachment
#        elif is_comment:    self.type = springnote.Comment
#        else:               self.type = springnote.Page
#        return self
#
#    def set_rev(self, value):
#        rev, rev_index = None, None
#        if value:
#            if any(map(value.startswith, ['-', '+'])):
#                rev_index = int(value)
#            else:
#                rev = int(value)
#        return rev, rev_index
#
#    def get_parent(self):
#        if self.parent_id:
#            return ResourcePointer(note=self.note, id=self.parent_id)


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

class SpringclCommand(object):
    _sn = None
    _remote_service = springnote.HttpRequestService()

    def sn(self, options, service=None):
        ''' return proper sn, according to options and service given '''
        options = options or self.options
        self._sn = self._sn or make_sn(options.auth, options.consumer)

        new_service = self._remote_service 
        service = service or new_service
        if isinstance(service, filesystem_service.FileSystemService) and options.basedir:
            service.base_dir = options.basedir

        # update service of sn 
        self._sn.service = service

        return self._sn

    def last_ran_service_was_remote(self):
        return isinstance(self._sn.service, springnote.HttpRequestService)

    def format(self, text):
        return text
    
    def write(self, text, output):
        f = sys.stdout if output is None else open(output, 'a')
        f.write(text)
        f.write("\n")
        if output:
            f.close()

    def find_page_id(self, arg, options):
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
        ''' try fetching resource from local, remote, or both, following options '''
        sn     = self.sn(options)
        result = fetch_method(sn)
        return result

