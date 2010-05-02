#!/usr/bin/python
'''
    Springcl Read Command Test
'''

import unittest
#import unittest_decorator as unittest
from hamcrest import *
from mocktest import *
import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import springcl, springcl_commands
from springcl_commands import ReadCommand

def _w(s): return s.split()
def at_least(**arguments):
    tuples = arguments.iteritems()
    lambda *args, **kwargs: all(map(lambda t: t in kwargs.iteritems(), tuples))

class OptionTestCase(TestCase):
    def get_options(self, opt_list):
        return ReadCommand(opt_list).options

class LocalRemoteOptionTestCase(OptionTestCase):
    def test_remote_option_sets_run__remote_to_true(self):
        options = self.get_options(_w("--remote 123"))
        # verify
        assert_that(options.run_remote, is_(True))
        assert_that(options.run_local,  is_(False))

    def test_local_option_sets_run__local_to_true(self):
        options = self.get_options(_w("--local 123"))
        #
        assert_that(options.run_remote, is_(False))
        assert_that(options.run_local,  is_(True))

    def test_remote_local_option_runs_remote_first_and_local_only_if_fail(self):
        options = self.get_options(_w("--remote-local 123"))
        # verify
        assert_that(options.run_remote,        is_(True))
        assert_that(options.run_local,         is_(False))
        assert_that(options.run_local_on_fail, is_(True))

    def test_remote_or_local_alone_does_not_set_run_local_on_fail(self):
        def run_local_on_fail_option_with(opt_str):
            return self.get_options(_w(opt_str)).run_local_on_fail
        assert_that(run_local_on_fail_option_with("--local 123"),  is_(False))
        assert_that(run_local_on_fail_option_with("--remote 123"), is_(False))

class TitleIdOptionTestCase(OptionTestCase):
    def test_title_option_force_is__title_to_true(self):
        options = self.get_options(_w("--title 123"))
        assert_that(options.is_title, is_(True))
    def test_id_option_force_is__id_to_true(self):
        options = self.get_options(_w("--id a123"))
        assert_that(options.is_id, is_(True))
    def test_neither_title_or_id_option_by_default(self):
        options = self.get_options(_w("123"))
        assert_that(options.is_id,    is_(False))
        assert_that(options.is_title, is_(False))

class NoteOptionTestCase(OptionTestCase):
    def test_note_option_sets_note(self):
        options = self.get_options(_w("--note jangxyz a123"))
        assert_that(options.note, is_('jangxyz'))
        assert_that(options.args, is_(_w('a123')))

    def test_note_option_defaults_to_none(self):
        options = self.get_options(_w("a123"))
        assert_that(options.note, is_(None))


class FetchPageLocalRemoteTestCase(TestCase):
    ''' test case for fetching resource from local, remote, or remote-then-local scenario '''
    def setUp(self): 
        self.get_page_remote_expected = mock_on(ReadCommand.sn_remote).get_page.is_expected
        self.get_page_local_expected  = mock_on(ReadCommand.sn_local).get_page.is_expected

    def tearDown(self): pass

    def stub_parse(self, **new_options):
        options = { # default
            'is_title': False,
            'is_id': False,
            'args': [], 
            'note': None,
        }
        options.update(new_options)
        option_mock = mock('option').with_children(**options).raw
        mock_on(ReadCommand).parse.is_expected.returning(option_mock)
    
    def test_access_remotely_with_remote_option(self):
        self.stub_parse(run_remote=True, run_local=False, args=[123])
        # only REMOTE should be called
        self.get_page_remote_expected.once()
        self.get_page_local_expected.no_times()
        ReadCommand().run()

    def test_access_locally_with_local_option(self):
        self.stub_parse(run_remote=False, run_local=True, args=[123])

        # only LOCAL should be called
        self.get_page_remote_expected.no_times()
        self.get_page_local_expected.once()
        ReadCommand().run()

    def test_access_remotely_then_locally_if_failed_given_remote_local_option(self):
        self.stub_parse(
            run_remote=True, 
            run_local=False, 
            run_local_on_fail=True, 
            args=[123])

        # call LOCAL if REMOTE fails
        exception = springcl_commands.springnote.SpringnoteError.NoNetwork('no network')
        self.get_page_remote_expected.once().raising(exception)
        self.get_page_local_expected.once()
        ReadCommand().run()

class FetchPageConvertTitleToIdTestCase(TestCase):
    ''' test case for converting given title into id '''

    def setUp(self):
        self.sn = mock_on(ReadCommand.sn_local)

    def stub_parse(self, **new_options):
        options = { # default
            'args': [], 
            'run_local': True,
            'run_remote': False, 
            'note': None,
        }
        options.update(new_options)
        option_mock = mock('option').with_children(**options).raw
        mock_on(ReadCommand).parse.is_expected.returning(option_mock)

    def test_is_title_option_searches_for_title_first_to_achieve_id(self):
        title = "some title"
        id_in_return = 123
        pages = [mock('page').with_children(id = id_in_return).raw]
        # mocks
        self.stub_parse(is_title=True, is_id=False, args=[title])
        self.sn.list_pages.is_expected.where_(at_least(title=title)) \
            .returning(pages)
        self.sn.get_page.is_expected.where_(at_least(id=id_in_return))
        # run
        ReadCommand().run()

    def test_is_title_option_raises_error_if_more_than_one_page_is_found(self):
        title = "some title"
        pages = [mock('page'), mock('page')]
        # mocks
        self.stub_parse(is_title=True, is_id=False, args=[title])
        self.sn.list_pages.is_expected.where_(at_least(title=title)).returning(pages)
        self.sn.get_page.is_not_expected # because exception will raise
        # run
        self.failUnlessRaises(springcl.DuplicateResources,
            lambda: ReadCommand().run())

    def test_is_title_option_raises_error_if_no_page_is_found(self):
        title = "some title"
        pages = []
        # mocks
        self.stub_parse(is_title=True, is_id=False, args=[title])
        self.sn.list_pages.is_expected.where_(at_least(title=title)) \
            .returning(pages)
        self.sn.get_page.is_not_expected # because exception will raise
        # run
        self.failUnlessRaises(springcl.NoSuchResource,
            lambda: ReadCommand().run())

    def test_is_id_option_raises_error_if_arg_is_not_numeric(self):
        title = "a123"
        # mocks
        self.stub_parse(is_title=False, is_id=True, args=[title])
        self.sn.get_page.is_not_expected # because exception will raise
        # run
        self.failUnlessRaises(springcl.OptionError,
            lambda: ReadCommand().run())

    def test_assumes_numeric_as_id_by_default(self):
        arg = "123"
        self.stub_parse(is_title=False, is_id=False, args=[arg])
        self.sn.get_page.is_expected.where_(at_least(id=int(arg)))
        ReadCommand().run()

    def test_assume_non_numeric_as_title_by_default(self):
        arg = "a123"
        id_in_return = 123
        pages = [mock('page').with_children(id = id_in_return).raw] # single page
        # mocks
        self.stub_parse(is_title=False, is_id=False, args=[arg])
        self.sn.list_pages.is_expected.where_(at_least(title=arg)) \
            .returning(pages)
        self.sn.get_page.is_expected.where_(at_least(id=id_in_return))
        ReadCommand().run()


class FetchPageWithNoteTestCase(TestCase):
    def setUp(self):
        self.sn = mock_on(ReadCommand.sn_local)

    def stub_parse(self, **new_options):
        options = { # default
            'is_title':  False, 'is_id': False,
            'run_local': True,  'run_remote': False,
        }
        options.update(new_options)
        option_mock = mock('option').with_children(**options).raw
        mock_on(ReadCommand).parse.is_expected.returning(option_mock)

    def test_note_option_sets_note_in_get_page(self):
        note, id = ('jangxyz', 123)
        # mock and run
        self.stub_parse(note=note, args=[id])
        self.sn.get_page.is_expected.with_args(id=id, note=note)
        ReadCommand().run()

    def test_note_option_sets_note_in_list_page_where_needed(self):
        note, title = ('jangxyz', "a123")
        pages = [mock('page').with_children(id=123).raw]
        # mocks
        self.stub_parse(note=note, args=[title])
        self.sn.list_pages.is_expected.with_(title=title, note=note).returning(pages)
        self.sn.get_page.is_expected
        # run
        ReadCommand().run()



if __name__ == '__main__':
    unittest.main()

