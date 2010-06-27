#!/usr/bin/python

__all__ = ['_w', 'L', 'D']

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
    def max(self, key=None):
        return max(self, key=key)

    def to_tuple(self):
        return tuple(self)

class D(dict):
    def updating(self, **kwargs):
        self.update(kwargs)
        return self


