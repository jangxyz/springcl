#!/usr/bin/python

import env
from config import Config
import simple_options
from springcl_commands import *
from util import *

from urlparse import urlparse
import os, shutil
from time import time

# read config
config = Config().load()

class InitCommand(SpringclCommand):
    usage = '''
        springcl init [OPTIONS] 
    ''' 
    options = '''
        --default-note NOTE  : tell default note to springcl
        --check-default-note    => is_check_default_note : check default note from springnote.com (remote)
        --no-check-default-note => is_check_default_note : do not check default note from springnote.com (remote)

        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = simple_options.parse(self.usage, self.options, opt_list)

    def run(self):
        print 'options:', self.options
        default_note = self.set_default_note()
        self.make_directories(default_note)

    def make_directories(self, default_note=None):
        print 'making directories under:', self.options.basedir
        # TODO: check permission denied, out of disk, no such file or directory

        # create base directory
        basedir = self.options.basedir
        ensure_directory(basedir)

        if default_note:
            # create note directory
            ensure_directory(os.path.join(basedir, default_note))

            # create symlink to default note directory
            ensure_symlink(basedir, default_note, 'default')



    def set_default_note(self):
        ''' figure out level of setting default note from options and config

        three variables: (local/remote, known/unknown, option)

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

        print 'default note:', 
        if config.has(DEFAULT_NOTE_OPT):
            print config.get(DEFAULT_NOTE_OPT, section=DEFAULT_NOTE_SEC)
        else:
            print 'not set'
        default_value = config.get(DEFAULT_NOTE_OPT, section=DEFAULT_NOTE_SEC, default=None)

        # --default-note
        if options.default_note is not None:
            print '--default-note:', options.default_note
            self.update_config(DEFAULT_NOTE_OPT, DEFAULT_NOTE_SEC, options.default_note)
            return options.default_note

        # local
        is_local_only = not options.run_remote
        if is_local_only:
            print "local only. can't do anything really."
            return default_value

        # --no-check-default-note
        if options.is_check_default_note is False:
            print 'do not check default note.'
            return default_value

        # --check-default-note
        if options.is_check_default_note is not False:
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


def merge(src, dst, workpath):
    ''' copy all files in src to dst atomically '''
    try:
        copytree_multisrc(srcs=[src, dst], dst=workpath)
        shutil.rmtree(dst)
        shutil.move(workpath, dst)
    except e:
        print 'failed during merge. working copy is saved at:', workpath
        raise e


def copytree_multisrc(srcs, dst):
    ''' variant of shutil.copytree, having multiple sources '''
    ensure_directory(dst)

    # find filenames of existing path
    names = L(srcs)                                               \
        .filter(lambda p: os.path.exists(p) and os.path.isdir(p)) \
        .map(os.listdir)                                          \
        .reduce(lambda x,y: x+y)

    for name in set(names):
        src_names = map(lambda x: os.path.join(x, name), srcs)
        dstname   = os.path.join(dst, name)
        # choose source to copy
        name = L(src_names) \
                    .filter(os.path.exists) \
                    .max(key=lambda x: os.stat(x).st_ctime)
        try:
            if os.path.islink(name):  os.symlink(os.readlink(name), dstname)
            elif os.path.isdir(name): copytree_multisrc(src_names, dstname)
            else:                     shutil.copy2(name, dstname)
        except (IOError, os.error), why:
            print "Can't copy %s to %s: %s" % (`name`, `dstname`, str(why))
            raise why

def ensure_directory(path):
    ''' only directory should remain after this command '''
    if not os.path.exists(path):
        os.makedirs(path)
    elif not os.path.isdir(path):
        print path, "is not a directory!"
        return

def ensure_symlink(basepath, link_src, new_link):
    tmp_path = os.path.join(basepath, '.tmp')
    curdir = os.path.abspath(os.path.curdir)
    try:
        os.chdir(basepath)

        if os.path.exists(new_link):
            workpath = os.path.join(tmp_path, str(int(time())))
            # linked correctly
            if os.path.islink(new_link) and os.readlink(new_link) == link_src:
                return
            # linked to a wrong directory - merge and relink
            elif os.path.islink(new_link):
                merge(new_link, os.readlink(new_link), workpath)
                os.unlink(new_link)
            # already used as a directory - merge and link
            elif os.path.isdir(new_link):
                merge(new_link, link_src, workpath)
                shutil.rmtree(new_link)
            # a file? why?
            else:
                raise 'neither a link or directory'
        # link
        os.symlink(link_src, new_link)
    finally:
        if os.path.exists(tmp_path) and len(os.listdir(tmp_path)) == 0:
            os.rmdir(tmp_path)
        os.chdir(curdir)


if __name__ == '__main__':
    InitCommand().run()    


