#!/usr/bin/python

"""

    File System Service

        replacement of HttpRequestService in springnote library,
        to locally fetch resource instead from springnote.com

"""
import urllib, httplib, os
BASE_PATH = "~/.springcl"

class FileNotExist(Exception): pass

class FileSystemService:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    @staticmethod
    def query_dict(query):
        return dict(map(urllib.splitvalue, query.split('&')))

    def parse_url(self, url):
        ''' parse url and convert it to filesystem path: $BASE_DIR/domain/page_id/

        list (omitting host http://api.springnote.com/)
         * /pages.json                    => /default/
         * /pages.json?domain=jangxyz     => /jangxyz/
         * /pages/563954/revisions.json   => /default/563954/revisions/
         * /pages/563954/attachments.json => /default/563954/attachments/

        get
         * /pages/563954.json?domain=jangxyz     => /jangxyz/563954/563954.json
         * /pages/563954/revisions/29685883.json => /default/563954/revisions/29685883.json
         * /pages/563954/attachments/559756.json => /default/563954/attachments/559756.json
        '''
        # extract path and query from url
        _scheme, _netloc, path, query, _fragment = httplib.urlsplit(url)

        # domain
        domain   = self.query_dict(query).get('domain', 'default')
        filepath = os.path.join(self.base_dir, domain)

        # build path
        resource, last_resource, id = None, None, None
        path, _sep, format = path.partition('.')
        l = filter(None, path.split('/'))
        for resource, id in zip(l[::2], l[1::2] + [None]):
            if resource != "pages": filepath = os.path.join(filepath, resource)
            if id is not None:      filepath = os.path.join(filepath, id)
            last_resource = resource
        if id is not None:
            if "pages" == last_resource:  filepath = os.path.join(filepath, id)
            if format:                    filepath += '.' + format

        return filepath

    def request(self, method, url, body=None, verbose=None, **kwarg):
        ''' request resource to local file system, returning in json format '''
        if "GET" == method:
            filepath = self.parse_url(url)
            if not os.path.exists(filepath):
                raise FileNotExist("%s does not exist" % filepath)

            if os.path.isdir(filepath): return self.format_dir_entries(filepath)
            else:                       return self.readfile(filepath)
        else:
            raise NotImlementedError("not yet")

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
    


if __name__ == '__main__':
    pass

