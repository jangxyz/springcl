import env
import springnote, filesystem_service
from util import *
from config import *

config = Config().load()
logger = get_logger(__file__, level='info')

import os, sys
import logging
import simple_options

CONSUMER_TOKEN  = '5aUy7Iz0Rf7RHFflaY2kNQ'
CONSUMER_SECRET = 'oOTGX5p8v0bmPa2csaprPTbrpbSmEC17Yscn88sSJg'

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

def classname2commandname(name):
    ''' ReadPageCommand -> read-page '''
    return ''.join(
        map(
            lambda ch: '-' + ch.lower() if ch.isupper() else ch, 
            list(name.partition('Command')[0])
        )
    ).lstrip('-')
        
def modulename2classname(name):
    ''' read_page_command -> ReadPageCommand '''
    return ''.join(
        map(lambda x: x.title(), name.split('_'))
    )
    

def make_sn(auth, consumer=None):
    consumer = consumer or (CONSUMER_TOKEN, CONSUMER_SECRET)
    if ':' in auth:
        auth = auth.split(':')
    sn = springnote.Springnote(access_token=auth, consumer_token=consumer)
    #if auth:
    #    sn.set_access_token(auth)
    return sn

class SpringclCommand(object):
    _sn = None
    _remote_service = springnote.HttpRequestService
    _local_service  = filesystem_service.FileSystemService('~/.springcl')

    @classmethod
    def parse(cls, arg_list=[], options=None, usage=None):
        ''' read `usage` and `options` from class and build simple_option parser 
        use configuration file as default value '''
        assert 'usage' in vars(cls) and 'options' in vars(cls)
        parser = simple_options.Parser(cls.usage, cls.options, 
            defaults=config.to_dict())
        options = parser.parse(arg_list)
        logger.debug(options)
        return options

    @classmethod
    def option_names(cls):
        ''' return list of names of options for the class '''
        options = cls.parse()
        return options.__dict__.keys()

    def sn(self, options, service=None, run_local=None):
        ''' return proper sn, according to options and service given '''
        options = options or self.options
        if run_local is None:
            run_local = options.run_local

        # make sn
        sn = make_sn(options.auth.split(':'), options.consumer.split(':'))
        if run_local:
            sn.service = filesystem_service.FileSystemService(options.basedir)

        return sn

    def last_ran_service_was_remote(self):
        return isinstance(self._sn.service, springnote.HttpRequestService)

    def format(self, text):
        return text
    
    def write(self, text, output):
        f = sys.stdout if output is None else open(output, 'w')
        f.write(text)
        f.write("\n")
        if output:
            f.close()

    def try_fetch(self, fetch_method, options={}, run_local=None):
        ''' try fetching resource from local, remote, or both, following options '''
        options   = options or self.options
        run_local = options.run_local if run_local is None else run_local

        try:
            sn = self.sn(options, run_local=run_local)
            result = fetch_method(sn)
            # save whether fetched from remote on success
            self.fetched_from_remote = sn.service is springnote.HttpRequestService
            return result
        except Exception, e:
            next_run_local = None
            # local --> remote
            if run_local and options.run_remote_on_fail:
                next_run_local = False
            # remote --> local
            if not run_local and options.run_local_on_fail:
                next_run_local = True

            fetch_mode = lambda run_local: 'local' if run_local else 'remote'

            logger.info('%s failed' % fetch_mode(run_local))
            if next_run_local is not None:
                logger.info('trying %s' % fetch_mode(next_run_local))
                return self.try_fetch(fetch_method, run_local=next_run_local)
            else:
                raise e

if __name__ == '__main__':
    pass
