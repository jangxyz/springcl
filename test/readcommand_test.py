#!/usr/bin/python
'''
    Springcl Read Command Test
'''

# testing modules
import unittest_decorator_patch as unittest
from hamcrest import *
from mocktest import *
import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import types
from global_options_test import OptionTestCase

# springcl
import springcl, springcl_commands
from springcl_commands.read_command import ReadCommand, simple_options
from springcl_commands import Errors as error
import springnote

# services
from filesystem_service import FileSystemService, FileNotExist
from springnote import HttpRequestService

def _w(s): return s.split()
def at_least(**arguments):
    tuples = arguments.iteritems()
    lambda *args, **kwargs: all(map(lambda t: t in kwargs.iteritems(), tuples))

def is_local_service(service):
    return isinstance(service, FileSystemService)
def is_remote_service(service):
    return isinstance(service, HttpRequestService)

def should_expect_Page_list(returns, *args, **kwargs):
    list_wrapper = mock('Page.list').is_expected \
        .where_(at_least(**kwargs))              \
        .returning(returns)                      \
        ._mock_wrapper
    mock_on(springnote).Page.with_children(list=list_wrapper.raw)
    return mock_on(springnote).Page

def should_expect_page_get(returns=None, *args, **kwargs):
    # page.get() mock
    page_get = mock('page.get').is_expected._mock_wrapper
    if returns is not None:
        page_get.returning(returns)
    # Page() instance mock
    page_instance = mock('page instance').with_children(get=page_get.raw)

    #return should_expect_page(page_instance.raw)
    mock_on(springnote).Page.is_expected.once() \
        .where_(at_least(**kwargs))             \
        .returning(page_instance.raw)
    return mock_on(springnote).Page

default_options = {
    'is_title': False, 'is_id': False,
    'run_local': True, 'run_remote': False, 
    'args': [123], 'note': None,
    'rev': None,
    'is_comment': False,
    'is_path': False,
    'basedir': None,
    'output': '/dev/null',
    'auth': None,
    'consumer': None,
}

class StopTesting(Exception): pass

class TitleIdOptionTestCase(OptionTestCase):
    def test_title_option_force_is__title_to_true(self):
        options = self.get_options("--title 123")
        assert_that(options.is_title, is_(True))
    def test_id_option_force_is__id_to_true(self):
        options = self.get_options("--id a123")
        assert_that(options.is_id, is_(True))
    def test_neither_title_or_id_option_by_default(self):
        options = self.get_options("123")
        assert_that(options.is_id,    is_(False))
        assert_that(options.is_title, is_(False))

class NoteOptionTestCase(OptionTestCase):
    def test_note_option_sets_note_name(self):
        options = self.get_options("--note jangxyz a123")
        assert_that(options.note, is_('jangxyz'))
        assert_that(options.args, is_(['a123']))

    def test_note_option_defaults_to_none(self):
        options = self.get_options("a123")
        assert_that(options.note, is_(None))

class RevOptionTestCase(OptionTestCase):
    def test_rev_option_sets_rev_as_string(self):
        def rev_option_with(opt_str):
            return self.get_options(opt_str + " 563954").rev
        assert_that(rev_option_with("--rev  1"), is_( '1')) #  1 differs with
        assert_that(rev_option_with("--rev +1"), is_('+1')) # +1
        assert_that(rev_option_with("--rev -1"), is_('-1'))

class OutputOptionTestCase(OptionTestCase):
    def test_output_option_sets_output_file(self):
        options = self.get_options("--output result.out 563954")
        assert_that(options.output, is_('result.out'))

    def test_output_option_defaults_to_none(self):
        options = self.get_options("563954")
        assert_that(options.output, is_(None))

class AuthOptionTestCase(OptionTestCase):
    def test_auth__option_sets_access_token(self):
        options = self.get_options("--auth ACCESS_TOKEN:SECRET 563954")
        assert_that(options.auth, is_(("ACCESS_TOKEN", "SECRET")))

    def test_consumer__option_sets_access_token(self):
        options = self.get_options("--consumer CONSUMER_TOKEN:SECRET 563954")
        assert_that(options.consumer, is_(("CONSUMER_TOKEN", "SECRET")))

    def test_default__consumer__option(self):
        options = self.get_options("563954")
        assert_that(options.consumer[0], is_(springcl_commands.CONSUMER_TOKEN))
        assert_that(options.consumer[1], is_(springcl_commands.CONSUMER_SECRET))


######
#
######

class LoadSn(TestCase):
    def setUp(self):
        self.page = mock('page').with_children(raw='RAW').raw

    def run_command(self):
        mock_on(ReadCommand).format.returning('RAW') # stub out format
        ReadCommand(['123']).run()

    def test_loads_sn(self):
        mock_on(springnote).Springnote.is_expected.raising(StopTesting)
        self.assertRaises(StopTesting, lambda: self.run_command())

    def test_calls_Page_with_sn(self):
        sn_is_first_arg = lambda *args, **kw: isinstance(args[0], springnote.Springnote)
        mock_on(springnote).Page.is_expected.where_(sn_is_first_arg).once()
        self.run_command()

    def test_page_calls_get(self):
        mock_on(springnote.Page).get.is_expected.once()
        self.run_command()



class FetchPageLocalRemoteTestCase(TestCase):
    ''' test case for fetching resource from either local or remote, depending 
    on the precedence option.

    options:
     * run_local
     * run_remote
     * run_local_on_fail
     * run_remote_on_fail
    '''
    def run_command(self, text='RAW'):
        mock_on(ReadCommand).format.returning(text)
        ReadCommand().run()

    def stub_parse(self, **new_options):
        options = default_options.copy()
        options.pop('run_local')
        options.pop('run_remote')
        options.update(new_options)
        if options.get('run_local'):   options['run_remote'] = False
        if options.get('run_remote'):  options['run_local']  = False
        option_mock = mock('option').with_children(**options).raw

        mock_on(ReadOption).parse.is_expected.returning(option_mock)

    def stub_update_local_cache(self):
        mock_on(ReadCommand).update_local_cache

    def test_access_locally_with_local_option(self):
        ''' sn.service used in Page.get is instance of FileSystemService '''
        self.stub_parse(run_local=True, run_remote_on_fail=False)

        sn_has_local_service = lambda *args, **kw: is_local_service(args[0].service)
        mock_on(springnote).Page.is_expected.once().where_(sn_has_local_service)

        self.run_command()

    def test_access_remote_after_local_if_not_found(self):
        self.stub_parse(run_local=True, run_remote_on_fail=True)
        self.stub_update_local_cache()

        self.prev_service_called = None
        def sn_has_local_then_remote_service(*args, **kw):
            ''' return True only if 1st call has local service and 2nd remote '''
            service = args[0].service

            if self.prev_service_called is None:
                is_correct_type = is_local_service(service)
            elif is_local_service(self.prev_service_called):
                is_correct_type = is_remote_service(service)
            else: self.fail("not allowed: %s after %s" % (service, self.prev_service_called))

            self.prev_service_called = service
            return is_correct_type
        def raise_exception_only_at_local(*args, **kwargs):
            if is_local_service( args[0].service): 
                raise FileNotExist
            if is_remote_service(args[0].service): 
                m_Page = mock('Page mock').with_methods('get').raw
                return m_Page
            self.fail("%s is not an allowed type" % type(args[0].service))

        mock_on(springnote).Page.is_expected.twice()    \
            .where_(sn_has_local_then_remote_service)   \
            .with_action(raise_exception_only_at_local)

        self.run_command()


    def test_access_remotely_with_remote_option(self):
        self.stub_parse(run_remote=True)
        self.stub_update_local_cache()

        ## only REMOTE should be called
        sn_has_remote_service = lambda *args, **kw: is_remote_service(args[0].service)
        mock_on(springnote).Page.is_expected.once() \
            .where_(sn_has_remote_service)          \
            .raising(StopTesting)

        self.assertRaises(StopTesting, lambda: self.run_command())

    def test_get_page_remotely_then_locally_if_failed_given_remote_local_option(self):
        self.stub_parse(run_remote=True, run_local_on_fail=True)

        # call LOCAL if REMOTE fails
        self.prev_service_called = None
        def sn_has_remote_then_local_service(*args, **kw):
            ''' return True only if 1st call has local service and 2nd remote '''
            service = args[0].service

            if self.prev_service_called is None:
                is_correct_type = is_remote_service(service)
            elif is_remote_service(self.prev_service_called):
                is_correct_type = is_local_service(service)
            else: self.fail("not allowed: %s after %s" % (service, self.prev_service_called))

            self.prev_service_called = service
            return is_correct_type
        def raise_exception_only_at_remote(*args, **kwargs):
            if is_remote_service(args[0].service): 
                raise springnote.SpringnoteError.NoNetwork("no network")
            elif is_local_service(args[0].service): 
                return mock('page').with_methods('get').raw
            else: self.fail("%s is not an allowed type" % type(args[0].service))

        mock_on(springnote).Page.is_expected.twice()  \
            .where_(sn_has_remote_then_local_service) \
            .with_action(raise_exception_only_at_remote)

        self.run_command()


class FetchPageConvertTitleToIdTestCase(TestCase):
    ''' test case for converting given title into id '''
    def run_command(self, text='RAW'):
        mock_on(ReadCommand).format.returning(text)
        ReadCommand().run()

    def stub_parse(self, **new_options):
        options = default_options.copy()
        options.update(args=[])
        options.update(new_options)
        if options.get('run_local'):   
            options.update({'run_remote': False, 'run_remote_on_fail': False})
        if options.get('run_remote'):  
            options.update({'run_local': False, 'run_local_on_fail': False})
        option_mock = mock('option').with_children(**options).raw
        mock_on(ReadOption).parse.is_expected.returning(option_mock)


    def test_is_title_option_searches_for_title_first_to_achieve_id(self):
        ''' "--title TITLE" calls Page.list(title=TITLE) and then Page(id=ID).get() '''
        title = "some title"
        id_in_return = 123
        self.stub_parse(is_title=True, is_id=False, args=[title])
        page = mock('page').with_children(id=id_in_return)

        should_expect_Page_list(title=title, returns=[page.raw])
        should_expect_page_get(id=id_in_return)

        self.run_command()

    def test_is_title__option_raises_error_if_more_than_one_page_is_found(self):
        title = "some title"
        pages = [mock('page'), mock('page')]

        # mocks
        self.stub_parse(is_title=True, is_id=False, args=[title])
        should_expect_Page_list(title=title, returns=pages)
        mock_on(springnote).Page.is_expected.no_times()

        # run
        self.failUnlessRaises(error.DuplicateResources, lambda: self.run_command())


    def test_is_title__option_raises_error_if_no_page_is_found(self):
        title = "some title"
        pages = []

        # mocks
        self.stub_parse(is_title=True, is_id=False, args=[title])
        should_expect_Page_list(title=title, returns=pages)
        mock_on(springnote).Page.is_expected.no_times()

        # run
        self.failUnlessRaises(error.NoSuchResource, lambda: self.run_command())

    def test_is_id_option_raises_error_if_arg_is_not_numeric(self):
        title = "a123"
        self.stub_parse(is_title=False, is_id=True, args=[title])

        mock_on(springnote).Page.is_expected.no_times() # exception will raise

        # run
        self.failUnlessRaises(error.OptionError, lambda: self.run_command())

    def test_assumes_numeric_as_id_by_default(self):
        arg = "123"
        self.stub_parse(is_title=False, is_id=False, args=[arg])

        mock_on(springnote).Page.is_expected.where_(at_least(id=int(arg)))
        self.run_command()

    def test_assumes_non_numeric_as_title_by_default(self):
        arg = "a123"
        id_in_return = 123
        page = mock('page').with_children(id=id_in_return) # single page

        # mocks
        self.stub_parse(is_title=False, is_id=False, args=[arg])
        should_expect_Page_list(title=arg, returns=[page.raw])
        should_expect_page_get(id=id_in_return)

        # run
        self.run_command()


class FetchPageWithNoteTestCase(TestCase):
    def run_command(self):
        self.stub_format()
        ReadCommand().run()

    def stub_parse(self, **new_options):
        options = default_options.copy()
        options.update(new_options)
        option_mock = mock('option').with_children(**options).raw
        mock_on(ReadOption).parse.is_expected.returning(option_mock)

    def stub_format(self, text='RAW'):
        mock_on(ReadCommand).format.returning(text)

    def test_note__option_sets_note_in_get_page(self):
        note, id = ('jangxyz', 123)
        # mock and run
        self.stub_parse(note=note, args=[id])
        should_expect_page_get(id=id, note=note)
        self.run_command()

    def test_note_option_sets_note_in_list_page_where_needed(self):
        note, title = ('jangxyz', "a123")
        pages = [mock('page').with_children(id=123).raw]

        # mocks
        self.stub_parse(note=note, args=[title])
        should_expect_Page_list(title=title, note=note, returns=pages)
        should_expect_page_get()

        self.run_command()


class FetchPageWithRevisionTestCase(TestCase):
    def run_command(self):
        self.stub_format()  # stub out format
        ReadCommand().run()

    def stub_parse(self, **new_options):
        options = default_options.copy()
        options.update(args=[])
        options.update(new_options)
        option_mock = mock('option').with_children(**options).raw
        #mock_on(ReadOption).parse.is_expected.returning(option_mock)
        mock_on(simple_options).parse.is_expected.returning(option_mock)

    def stub_format(self, text='RAW'):
        mock_on(ReadCommand).format.returning(text)

    def test_numeric_rev_option_fetches_page_revision_with_id(self):
        id     =  123
        rev_id = '456'

        # mocks
        self.stub_parse(rev=rev_id, args=[id])

        page_get_revision = mock('page.get_revision')
        page_get_revision.is_expected.with_(id=rev_id)
        page_got = mock('page').with_children(get_revision=page_get_revision.raw)
        should_expect_page_get(id=id, returns=page_got.raw)

        self.run_command()

    
    def test_plus_signed_rev_option_fetches_page_revision_with_index(self):
        id, rev_idx = (123, '+3')
        # 
        self.stub_parse(rev=rev_idx, args=[id])

        page_get_revision = mock('page.get_revision')
        page_get_revision.is_expected.with_args(index=rev_idx)
        page_got = mock('page').with_children(get_revision=page_get_revision.raw)
        should_expect_page_get(id=id, returns=page_got.raw)

        self.run_command()

    @unittest.testonly
    def test_minus_signed_rev_option_fetches_page_revision_with_index(self):
        id, rev_idx = (123, '-2')
        # 
        self.stub_parse(rev=rev_idx, args=[id])

        page_get_revision = mock('page.get_revision')
        page_get_revision.is_expected.with_args(index=rev_idx)
        page_got = mock('page').with_children(get_revision=page_get_revision.raw)
        should_expect_page_get(id=id, returns=page_got.raw)

        self.run_command()

class ReadPathCommandTestCase(TestCase):
    def run_command(self):
        mock_on(ReadCommand).format.returning(text)
        ReadCommand().run()

    def stub_parse(self, **new_options):
        options = default_options.copy()
        options.update(new_options)
        option_mock = mock('option').with_children(**options).raw
        mock_on(ReadOption).parse.is_expected.returning(option_mock)

    #def test_local_page(self):       pass 
    #def test_local_revision(self):   pass 
    #def test_local_attachment(self): pass 
    #def test_local_comments(self):   pass 
    #def test_remote_page(self):       pass 
    #def test_remote_revision(self):   pass 
    #def test_remote_attachment(self): pass 
    #def test_remote_comments(self):   pass 


class AuthRemoteTestCase(TestCase):
    def stub_parse(self, **new_options):
        options = default_options.copy()
        options.update(new_options)
        option_mock = mock('option').with_children(**options).raw
        #mock_on(ReadOption).parse.is_expected.returning(option_mock)
        mock_on(simple_options).parse.is_expected.returning(option_mock)


    def run_command(self):
        ReadCommand(['123']).run()

    @unittest.testonly
    def test_use_access_token_when_calling_remote(self):
        access_token = ('ACCESS', 'TOKEN')

        def access_token_is_used(*args, **kwargs):
            token = kwargs['sign_token']
            return (token.key, token.secret) == access_token

        # mock
        self.stub_parse(auth=access_token)
        mock_on(springnote.Springnote).oauth_request.is_expected \
            .where_(access_token_is_used).raising(StopTesting)

        # run
        mock_on(ReadCommand).format.returning('RAW')
        self.assertRaises(StopTesting, lambda: self.run_command())


    def test_use_access_token_when_calling_remote(self):
        consumer_token = ('CONSUMER', 'TOKEN')

        def consumer_token_is_used(*args, **kwargs):
            token = args[0]
            return (token.key, token.secret) == consumer_token 

        # mock
        self.stub_parse(consumer=consumer_token)
        mock_on(springnote.oauth.OAuthRequest) \
            .from_consumer_and_token.is_expected  \
            .where_(consumer_token_is_used).raising(StopTesting)

        # run
        mock_on(ReadCommand).format.returning('RAW')
        self.assertRaises(StopTesting, lambda: self.run_command())

class UpdateRemoteResourceTestCase(TestCase):
    def test_exits_when_cannot_connect_to_remote(self):
        pass

    def test_exits_when_cannot_fetch_from_remote(self):
        pass


if __name__ == '__main__':
    unittest.main()

