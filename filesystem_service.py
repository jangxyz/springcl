#!/usr/bin/python

"""

    File System Service

        replacement of HttpRequestService in springnote library,
        to locally fetch resource instead from springnote.com

"""
import urllib, httplib, os

DEFAULT_NOTE_DIRNAME = 'default'


class FileNotExist(Exception): pass

class Service:
    def __init__(self): self.status = None
    def request(self):  raise NotImplementedError('inherit me!')
    def read(self):     raise NotImplementedError('inherit me!')

class FileSystemService(Service):
    ''' has request(), status, read() '''
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.filepath = None

    @staticmethod
    def query_dict(query):
        return dict(map(urllib.splitvalue, query.split('&')))

    def parse_url(self, url):
        ''' parse url and convert it to filesystem path: $BASE_DIR/domain/page_id/

        list (omitting host http://api.springnote.com/)
         * /pages.json                    => /default/
         * /pages.json?domain=jangxyz     => /jangxyz/
         * /pages/563954/revisions.json   => /default/pages/563954/revisions/
         * /pages/563954/attachments.json => /default/pages/563954/attachments/
         * /pages/563954/comments.json    => /default/pages/563954/comments/

        get
         * /pages/563954.json?domain=jangxyz     => /jangxyz/pages/563954/563954/json
         * /pages/563954/revisions/29685883.json => /default/pages/563954/revisions/29685883/json
         * /pages/563954/attachments/559756.json => /default/pages/563954/attachments/559756/json
         * /pages/563954/attachments/559756      => /default/pages/563954/attachments/559756/file
        '''
        # extract path and query from url
        _scheme, _netloc, path, query, _fragment = httplib.urlsplit(url)
        domain = self.query_dict(query).get('domain')

        # build path
        path, _sep, format = path.partition('.')
        id = (path.split('/', 3) + [None]*3)[2]

        resource_dict = {}
        l = filter(None, path.split('/'))
        for resource, rsrc_id in zip(l[::2], l[1::2] + [None]):
            resource_dict[resource] = rsrc_id or True
        resource_dict.pop('pages')

        return self.build_path(id, domain, format, **resource_dict)


    def build_path(self, id, note=None, format=None, **resources):
        '''
         revision or attachment should be None, True, or its resource id

         * (id=None, note=None)     /default/
         * (id=None)                /jangxyz/
         *                          /jangxyz/pages/563954/563954/json
         * ({revisions=True})       /default/pages/563954/revisions/
         * ({attachments=True})     /default/pages/563954/attachments/
         * ({revisions=29685883})   /default/pages/563954/revisions/29685883/json
         * ({attachments=559756)})  /default/pages/563954/attachments/559756/json
        '''
        note = note or DEFAULT_NOTE_DIRNAME
        if format is None: format = 'json'
        for non_key in filter(lambda k: resources[k] is None, resources):
            del resources[non_key]

        # /jangxyz
        filepath = os.path.join(self.base_dir, note) + os.path.sep

        # LIST pages
        if not id: return filepath

        # /jangxyz/563954
        filepath += "pages/%(id)s/" % locals()

        # GET page: /jangxyz/563954/563954.json
        if len(resources) is 0:
            filepath += format
        # subresources
        else:
            for rsrc_name, rsrc_id in resources.iteritems():
                # LIST
                filepath += "%(rsrc_name)s/" % locals()
                # GET
                if rsrc_id is not True:
                    if rsrc_name == 'attachments' and format == '':
                        filepath += "%(rsrc_id)s/file" % locals()
                    else:
                        filepath += "%(rsrc_id)s/%(format)s" % locals()

        return filepath

    def request(self, method, url, body=None, verbose=None, **kwarg):
        ''' request resource to local file system, returning in json format '''
        if "GET" == method:
            self.filepath = self.parse_url(url)
            # udpate status
            if os.path.exists(self.filepath):   self.status = httplib.OK
            else:                               self.status = httplib.NOT_FOUND

            return self

        else: raise NotImplementedError("not yet")

    def read(self):
        assert self.filepath, "should run after request()"
        if not os.path.exists(self.filepath):
            raise FileNotExist("%s does not exist" % self.filepath)

        if os.path.isdir(self.filepath):
            return self.format_dir_entries(self.filepath)
        else:
            return self.readfile(self.filepath)

    def format_dir_entries(self, path):
        ''' return entries inside directory as json format
            /note                     => every pages in note
            /note/PAGE_ID/revisions   => every revisions of page PAGE_ID
            /note/PAGE_ID/attachments => every attachments of page PAGE_ID
        '''
        if path.endswith('revisions'):
            files   = filter(lambda x: x.endswith('.json'), os.listdir(path))
        elif path.endswith('attachments'):
            files   = filter(lambda x: x.endswith('.json'), os.listdir(path))
        else:
            pages = filter(os.path.isdir, os.listdir(path))
            pages = map(lambda x: x.rstrip(os.path.sep), pages)
            pages = map(lambda x: os.path.join(x, os.path.basename(x)+".json"), pages)
            files = filter(os.path.exists, pages)

        return "[%s]" % ", ".join(map(self.readfile, files))

    def readfile(self, filename):
        return open(filename).read()


#import tempfile
#def merge(src, dest):
#    ''' merge between two directories:
#
#    1. create temp/ directory
#    2. copy all files from src/ and dest/ to temp/, where
#    3. choose newer if file with same name exists
#    4. backup dest/ for a moment,
#    5. remove dest/
#    6. rename temp/ to dest/
#    7. remove dest-backup/
#    8. if any error happens, restore dest-backup/
#    '''
#    if os.path.isfile(src):
#        return merge_file(src, dest)
#    tempdir = tempfile.mkdtemp()


def newer(*files):
    return max(files, key=os.path.getmtime)

def merge_file(src, dest, output=None):
    ''' the newer file among src and dest becomes dest, REMOVING src '''
    assert os.path.isfile(src)

    # dest is already a newer file
    if os.path.exists(dest) and newer(src, dest) is dest:
        os.remove(src)
        return

    # XXX: might have error on windows!
    os.rename(src, dest)


def merge_dir(src, dest):
    ''' merge directories src and dest, choosing the newer if same file exists 
    src is REMOVED. 
    '''
    assert os.path.exists(src) and os.path.isdir(src)
    if not os.path.exists(dest):
        os.makedirs(dest)
    if os.path.samefile(src, dest): return

    # merge contents inside
    for filename in os.listdir(src):
        src_file  = os.path.join(src,  filename)
        dest_file = os.path.join(dest, filename)

        if os.path.isdir(src_file): merge = merge_dir
        else:                       merge = merge_file
        merge(src_file, dest_file)

    # REMOVE src
    os.rmdir(src)

if __name__ == '__main__':
    pass

