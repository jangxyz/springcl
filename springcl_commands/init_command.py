#!/usr/bin/python

import env
from util import *

from springcl_commands import SpringclCommand

from fs.merge import ensure_directory, ensure_symlink
from urlparse import urlparse
import os

class InitCommand(SpringclCommand):
    usage = '''
        springcl init [OPTIONS] 
    ''' 
    options = '''
        --default-note NOTE  : tell default note to springcl
        #--check-default-note    => is_check_default_note : check default note from springnote.com (remote)
        #--no-check-default-note => is_check_default_note : do not check default note from springnote.com (remote)

        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = self.parse(opt_list)

    def run(self):
        print 'options:', self.options
        default_note = self.set_default_note()
        self.make_directories(default_note)

    def make_directories(self, default_note=None):
        ''' setup directories for local caching
        creates base directory, and if default note is known:
          - create default note directory, and
            pages/ and pages/titles/ under it
          - create a symlink default@ to the default note directory,
            merge if default/ already exists
        '''
        print 'making directories under:', self.options.basedir
        # TODO: check permission denied, out of disk, no such file or directory

        # create base directory
        basedir = self.options.basedir
        ensure_directory(basedir)

        if default_note:
            # create note directory
            ensure_directory("%(basedir)s/%(default_note)s/pages/titles" % locals())

            # create symlink to default note directory
            ensure_symlink(basedir, default_note, 'default')


    def set_default_note(self):
        ''' figure out level of setting default note from options and config

        three decisions: (local/remote, known/unknown, option)

        local: cannot set default note (except --default-note NOTE)
        remote: always try to set (except --no-check-default-note)
        * we don't consider local-only and remote-only here

        known: remote trys to set anyway.
        unknown: tries to set (except local and --no-check-default-note)

        --check-default-note: tries to check default note (except local)
        --no-check-default-note: does not check default note
        --default-note NOTE: directly sets default note
        '''
        options = self.options
        DEFAULT_NOTE_SEC, DEFAULT_NOTE_OPT = 'user', 'default_note'

        print 'default note:', options.default_note or "not set"
        default_value = options.default_note

        # --default-note given
        if options.default_note is not None:
            print '--default-note:', options.default_note
            self.update_config(DEFAULT_NOTE_OPT, DEFAULT_NOTE_SEC, options.default_note)
            return options.default_note

        # ignore when local
        is_local_only = not options.run_remote
        if is_local_only:
            print "local only. can't do anything really."
            return default_value

        # fetch default note from remote
        print 'checking default note...'
        default_note = self.fetch_default_note()
        self.update_config(DEFAULT_NOTE_OPT, DEFAULT_NOTE_SEC, default_note)
        return default_note

    def fetch_default_note(self):
        ''' fetch page from springnote.com to figure out default note '''
        fetch_method = lambda sn: sn.list_pages(sort='date_created', count=1)[0]
        # fetch
        page = self.try_fetch(fetch_method, options=self.options)

        #page.creator
        domain = urlparse(page.uri).hostname.partition('.springnote.com')[0]
        return domain

    def fetch(self, sn):
        ''' fetch method to read default note from springnote.com '''
        pages = sn.list_pages(sort='date_created', count=1)
        assert len(pages) > 0, "no pages found"
        return pages[0]
    
    def update_config(self, option, section=None, value=None):
        print 'updating config (%(section)s:%(option)s) to %(value)s' % locals()
        print 'doing nothing yet...'


if __name__ == '__main__':
    InitCommand().run()    


