#!/usr/bin/python
from __future__ import with_statement

import env
from util import *
from springcl_commands import SpringclCommand
from create_command import CreatePageCommand
import fs.label

import os

logger = get_logger(__file__)

def create_opt_list(*args, **kwargs):
    return list(args) + ['='.join(kv) for kv in kwargs.items()]

class SyncCommand(SpringclCommand):
    usage = '''
        springcl sync [OPTIONS]
    '''
    options = '''
        [Global Options]
    '''
    def __init__(self, opt_list=[]):
        self.options = self.parse(opt_list)
        if self.options.file is None:
            raise Exception("should give file to create")

    def run(self):
        ''' figure out proper subcommand and delegate to it '''
        return SyncPage(options=self.options).run()

class SyncPageCommand(SpringclCommand):
    usage   = 'springcl sync-page [OPTIONS]'
    options = '[Global Options]'

    def __init__(self, opt_list=[], options=None):
        if options: self.options = options
        else:       self.options = self.parse(opt_list)
        if self.options.run_local:
            logger.error("ignoring --local, running remote")
            self.options.run_local  = False
            self.options.run_remote = True

    def run(self):
        print 'syncing..'
        self.sync_deleted_pages()
        self.sync_unborn_pages()
        self.sync_modified_pages()

    def sync_unborn_pages(self):
        ''' create unborn pages to springnote.com '''
        basedir = self.options.basedir
        logger.info('sync unborn pages at: ' + basedir)

        # 
        note_paths = L(os.listdir(basedir))             \
            .map(lambda f: os.path.join(basedir, f))    \
            .filter(os.path.isdir)                      \
            .reject(os.path.islink)

        for note_path in note_paths:
            unborn_path = fs.label.get_unborn_path(note_path)
            for unborn_file in os.listdir(unborn_path):
                # build options
                options = self.copy_options(CreatePageCommand, 
                    note      = os.path.basename(note_path),
                    file      = os.path.join(unborn_path, unborn_file),
                    parent_id = unborn_file.partition('_')[0] or None,
                )

                # run create page command
                cmd = CreatePageCommand(options=options)
                cmd.run()

                # remove unborn page on success
                fs.label.remove_unborn(os.path.join(unborn_path, unborn_file))


    def sync_modified_pages(self):
        print 'sync modified pages...'

    def sync_deleted_pages(self):
        print 'sync deleted pages...'

    def copy_options(self, dest_cmd_class, **kwargs):
        ''' build new option for destination command class '''
        from optparse import Values
        options = Values()
        cmd_options = dest_cmd_class.option_names()
        for key, value in self.options.__dict__.items():
            if key in cmd_options:
                setattr(options, key, value)
        for key, value in kwargs.items():
            setattr(options, key, value)
        return options


