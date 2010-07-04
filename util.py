#!/usr/bin/python

__all__ = [
    '_w', 'get_logger', 'empty',
    'L', 'D', 'ValueNotGiven', 
]

class ValueNotGiven: pass

def empty(l):
    return len(l) is 0

def _w(s):
    return s.split()

class L(list):
    def appending(self, item, when=None):
        if when is not None:
            if callable(when):
                when = when()
            if not when:
                return self
        self.append(item)
        return self

    def map(self, func):
        return L(map(func, self))
    def reduce(self, func):
        return reduce(func, self)
    def filter(self, func):
        return L(filter(func, self))
    def reject(self, func):
        return L(filter(lambda x: not func(x), self))
    def max(self, key=None):
        return max(self, key=key)

    def to_tuple(self):
        return tuple(self)

class D(dict):
    def updating(self, **kwargs):
        self.update(kwargs)
        return self


def get_logger(filepath, level='info'):
    import logging, os
    LEVELS = {
        'debug'   : logging.DEBUG,
        'info'    : logging.INFO,
        'warning' : logging.WARNING,
        'error'   : logging.ERROR,
        'critical': logging.CRITICAL,
    }
    level = LEVELS[level.lower()]

    # create logger
    filepath = filepath.partition(os.getcwd())[-1].lstrip('/')
    logger_name = os.path.splitext(filepath)[0].replace('/', '.')
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # add formatter to ch
    ch.setFormatter(formatter)
    
    # add ch to logger
    logger.addHandler(ch)

    return logger

