#!/usr/bin/python

# add home path(..) to sys.path
import os, sys
sys.path.insert(1, os.path.abspath(os.path.dirname(__file__) + '/..'))

if __name__ == '__main__':
    print sys.path

del os, sys
