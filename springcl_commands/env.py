#!/usr/bin/python

# add home path(..) to sys.path
import os, sys
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__) + '/..'))

# add path for springnote/ module to sys.path
sys.path.append( os.path.realpath(os.path.dirname(__file__) + '/../springnote') )

if __name__ == '__main__':
    print sys.path

del os, sys
