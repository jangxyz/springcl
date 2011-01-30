#!/usr/bin/python
        
# add this directory and parent to sys.path
import os, sys, inspect
dirname = os.path.dirname(__file__)
sys.path.append( dirname + '/..' )
sys.path.append( dirname )

from springcl_commands import SpringclCommand

__all__ = []
# search every .py file and load subclasses of SpringclCommand
for file in filter(lambda x: x.endswith('.py'), os.listdir(dirname)):
    if file == '__init__.py':
        continue
    module_name = file.partition('.py')[0]
    mod = __import__(module_name, globals(), locals())
    for cls_name in dir(mod):
        cls = getattr(mod, cls_name)
        if not inspect.isclass(cls):
            continue
        # set imported class
        if issubclass(cls, SpringclCommand):
            if cls_name not in __all__:
                locals()[cls_name] = cls
                __all__.append(cls_name)

# del
for var in dir():
    if var == 'inspect':
        continue
    if inspect.ismodule(locals()[var]):
        del locals()[var]
del inspect
del cls_name, module_name, file, var, dirname

from springcl_commands import *

