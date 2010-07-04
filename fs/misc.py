#!/usr/bin/python

"""
    simple helper methods
"""
from __future__ import with_statement

def read_file(filename):
    file = open(filename)
    content = file.read()
    file.close()
    return content

def write_file(filename, content):
    file = open(filename, 'w')
    file.write(content)
    file.close()
    return content


