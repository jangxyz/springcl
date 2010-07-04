#!/usr/bin/python

"""

    read & write label of content

"""
from __future__ import with_statement

from util import *
import os, shutil, time

LABELS = _w("UNBORN MODIFIED CONFLICT DELETED")
UNBORN    = "UNBORN"
MODIFIED  = "MODIFIED"
CONFLICT  = "CONFLICT"
DELETED   = "DELETED"

def get_unborn_path(note_path, filename=''):
    return os.path.join(note_path, 'pages/.unborn', filename)

def get_label_path(path, label):
    if label != UNBORN:
        return os.path.join(path, '.label', label.upper())
    else:
        return path

def read_label(path, label):
    assert label.upper() in LABELS, "%(label)s is not a valid LABEL"

    label_path = get_label_path(path, label)
    if not os.path.exists(label_path):
        return False
    
    with open(label_path) as f:
        return f.read()

def remove_label(path, label):
    assert label.upper() in LABELS, "%(label)s is not a valid LABEL"

    # remove file
    label_path = get_label_path(path, label)
    os.remove(label_path)

    # remove directory if empty
    label_dir = os.path.dirname(label_path)
    if empty(os.listdir(label_dir)):
        os.removedirs(label_dir)

def remove_unborn(path):
    return remove_label(path, UNBORN)


def set_label(path, label):
    label_path = get_label_path(path, label)
    with open(label_path, 'w') as f:
        f.write(label)
def label_modified(path):   set_label(path, get_label_path(path, MODIFIED))
def label_unborn(path):     set_label(path, get_label_path(path, UNBORN))
def label_conflict(path):   set_label(path, get_label_path(path, CONFLICT))
def label_deleted(path):    set_label(path, get_label_path(path, DELETED))

