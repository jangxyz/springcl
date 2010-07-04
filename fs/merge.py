#!/usr/bin/python

'''
    merge contents
'''
from __future__ import with_statement

import os, shutil, time

from util import *
logger = get_logger(__file__, level='info')

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
        logger.debug('creating directory: ' + path)
        os.makedirs(path)
    elif not os.path.isdir(path):
        logger.error(path + ' is not a directory!')
        return

def ensure_symlink(basepath, link_src, new_link):
    tmp_path = os.path.join(basepath, '.tmp')
    curdir = os.path.abspath(os.path.curdir)
    try:
        os.chdir(basepath)

        if os.path.exists(new_link):
            workpath = os.path.join(tmp_path, str(int(time.time())))
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
                raise 'neither a link or directory: %s' % new_link
        # link
        os.symlink(link_src, new_link)
    finally:
        if os.path.exists(tmp_path) and len(os.listdir(tmp_path)) == 0:
            os.rmdir(tmp_path)
        os.chdir(curdir)

