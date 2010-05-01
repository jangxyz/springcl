#!/usr/bin/python
'''
    File System Service 
'''

import unittest
#import unittest_decorator as unittest
from hamcrest import *
from mocktest import *
import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import filesystem_service
from filesystem_service import FileSystemService
import simplejson as json

class ParseUrlTestCase(unittest.TestCase):
    '''
        list (omitting host http://api.springnote.com/)
         * /pages.json                    => /default/
         * /pages.json?domain=jangxyz     => /jangxyz/
         * /pages/563954/revisions.json   => /default/563954/revisions/
         * /pages/563954/attachments.json => /default/563954/attachments/

        get
         * /pages/563954.json?domain=jangxyz     => /jangxyz/563954/563954.json
         * /pages/563954/revisions/29685883.json => /default/563954/revisions/29685883.json
         * /pages/563954/attachments/559756.json => /default/563954/attachments/559756.json
         * /pages/563954/attachments/559756      => /default/563954/attachments/559756
    '''
    def setUp(self):    
        self.service = FileSystemService("/home/jangxyz/.springcl")

    def parse(self, url):
        return self.service.parse_url(url)

    def test_parsed_url_starts_with_base_dir(self):
        url = "http://api.springnote.com/pages.json"
        assert_that(self.parse(url), starts_with("/home/jangxyz/.springcl/"))

    def test_list_page(self):
        url = "http://api.springnote.com/pages.json"
        assert_that(self.parse(url), ends_with("/default"))

    def test_list_page_with_domain(self):
        url = "http://api.springnote.com/pages.json?domain=jangxyz"
        assert_that(self.parse(url), ends_with("/jangxyz"))

    def test_get_page(self):
        url = "http://api.springnote.com/pages/563954.json?domain=jangxyz"
        assert_that(self.parse(url), ends_with("/jangxyz/563954/563954.json"))

    def test_list_revision(self):
        url = "/pages/563954/revisions.json"
        assert_that(self.parse(url), ends_with("/default/563954/revisions"))

    def test_get_revision(self):
        url = "/pages/563954/revisions/29685883.json"
        assert_that(self.parse(url), ends_with("/default/563954/revisions/29685883.json"))
    
    def test_list_attachment(self):
        url = "/pages/563954/attachments.json"
        assert_that(self.parse(url), ends_with("/default/563954/attachments"))

    def test_get_attachment(self):
        url = "/pages/563954/attachments/559756.json"
        assert_that(self.parse(url), ends_with("/default/563954/attachments/559756.json"))

    def test_download_attachment(self):
        url = "/pages/563954/attachments/559756"
        assert_that(self.parse(url), ends_with("/default/563954/attachments/559756"))

class FormatDirEntriesTestCase(TestCase):
    def setUp(self):    
        self.service = FileSystemService("/home/jangxyz/.springcl")

        # mocks
        self.os_listdir_expected = mock_on(filesystem_service.os).listdir.is_expected
        self.readfile_expected   = mock_on(FileSystemService).readfile.is_expected

    def stub_file_category(self, category):
        import os
        def stub_file_content(filename):
            id = os.path.basename(filename).partition('.')[0]
            return '{"%s": {"id": %s}}' % (category, id)
        return stub_file_content

    def ls_should_show(self, path, files):
        ''' os.listdir is expected to return `files` when asked with `path` '''
        self.os_listdir_expected.with_args(path).returning(files)

    def readfile_should_show(self, title, called):
        self.readfile_expected                             \
            .where_args(lambda arg: arg.endswith(".json")) \
            .exactly(called).times                         \
            .with_action(self.stub_file_category(title))

    def test_revision_dir(self):
        ''' read only .json files inside revision directory in json format '''
        path = "/home/page/3/revisions"
        have = ["1.json", "2.json", "3.json", "4.xml"]
        count = len(filter(lambda x: x.endswith(".json"), have))

        # set
        self.ls_should_show(path, files=have)
        self.readfile_should_show('revision', called=count)

        # run
        contents = self.service.format_dir_entries(path)
        assert_that(json.loads(contents), has_length(count))

    def test_attachment_dir(self):
        ''' read only .json files inside attachments directory in json format '''
        path = "/home/page/3/attachments"
        have = ["1.json", "2.json", "2"]
        count = len(filter(lambda x: x.endswith(".json"), have))

        # set
        self.ls_should_show(path, files=have)
        self.readfile_should_show('attachment', called=count)

        # run
        contents = self.service.format_dir_entries(path)
        assert_that(json.loads(contents), has_length(count))

    def test_all_pages_dir(self):
        """ read every json file in /ID/ID.json in pages directory """
        path   = "/springcl_home/note"
        subdir = ["1.json", "2.html", "3.json", "attachments/", "revisions/"]
        dir    = {'config': None, '1/': subdir, '2/': subdir }
        files = [dname + fname for dname in dir if dir[dname] for fname in dir[dname]]
        count = 1
        assert_that("1/1.json", is_in(files))
        assert_that("2/2.json", is_not(is_in(files)))
    
        # set
        ospath_isdir_expected = mock_on(filesystem_service.os.path).isdir.is_expected
        ospath_exist_expected = mock_on(filesystem_service.os.path).exists.is_expected

        self.os_listdir_expected.with_action(lambda x: dir.keys() if x == path else subdir)
        ospath_isdir_expected.with_action(lambda x: True if x.endswith('/') else False)
        ospath_exist_expected.with_action(lambda x: True if x in files else False)
        self.readfile_should_show('page', called=count)

        # run
        contents = self.service.format_dir_entries(path)
        assert_that(json.loads(contents), has_length(count))


class RequestGetTestCase(TestCase):
    ''' testing FileSystemService.request, with method 'GET' '''

    def setUp(self):
        self.path = "/some/path"
        
        self.service = FileSystemService("/home/jangxyz/.springcl")

        self.service_anchor = mock_on(self.service)
        self.service_anchor.parse_url.is_expected.returning(self.path)

    def set_file_exists(self, path, exists=True):
        mock_on(filesystem_service.os.path).exists.is_expected \
            .with_args(path)                                   \
            .returning(exists)

    def set_is_dir(self, path, is_dir=True):
        mock_on(filesystem_service.os.path).isdir.is_expected \
            .with_args(path)                                  \
            .returning(is_dir)

    def test_parses_url_into_filepath(self):
        # mock
        self.set_file_exists(self.path)
        self.service_anchor.readfile.is_expected.with_args(self.path)

        # run
        self.service.request("GET", "/some/url")

    def test_raise_exception_when_no_such_file(self):
        self.set_file_exists(self.path, False)
        # run
        self.failUnlessRaises(
            filesystem_service.FileNotExist,
            lambda: self.service.request("GET", "/some/url")
        )

    def test_reads_contents_in_directory_if_path_is_directory(self):
        # mock
        self.set_file_exists(self.path)
        self.set_is_dir(self.path, True)
        self.service_anchor.format_dir_entries.is_expected.with_args(self.path)

        # run
        self.service.request("GET", "/some/url")

    def test_read_single_file_if_path_is_not_a_directory(self):
        # mock
        self.set_file_exists(self.path)
        self.set_is_dir(self.path, False)
        self.service_anchor.readfile.is_expected.with_args(self.path)

        # run
        self.service.request("GET", "/some/url")



if __name__ == '__main__':
    unittest.main()

