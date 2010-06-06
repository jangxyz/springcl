#!/usr/bin/python
        
import os, sys
dirname = os.path.dirname(__file__)
sys.path.append( dirname + '/..' )
sys.path.append( dirname )

from springcl_commands import *

__all__ = []
# search every .py file and load subclasses of SpringclCommand
for file in filter(lambda x: x.endswith('.py'), os.listdir(dirname)):
    module_name = file.partition('.py')[0]
    class_name  = modulename2classname(module_name)

    try:
        mod = __import__(module_name, globals(), locals())
        cls = getattr(mod, class_name)
    except AttributeError:
        continue
    
    # set imported class
    if issubclass(cls, SpringclCommand):
        locals()[class_name] = cls
        __all__.append(class_name)

