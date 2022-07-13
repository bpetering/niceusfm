# -*- coding: UTF-8 -*-

import re

class Element:
    """Base class for all parser elements.

       The start and end positions **in the source text** are kept, 
       a) to provide better errors and debugging information
       b) to round-trip from parse tree to source text 
       """

    def __init__(self, start=None, end=None, *args, **kwargs):

        # Allow creation of elements without setting everything at once.
        if start != None and type(start) in (str, int):
            self.start = int(start)

        if end != None and type(end) in (str, int):
            self.end = int(end)

        for k in kwargs:
            setattr(self, k, kwargs[k])

    def get_range(self):
        return (self.start, self.end)

    # Every Element has two methods for retrieving contained text: 
    # get_text()    provides a 'cleaned', generally useful version, but preserves whitespace
    #               according to the spec
    # get_parsed()  round-trips back to the exact parsed string
    def get_text(self):
        return None 

    def get_parsed(self):
        return None

    def overlaps(self, other):
        """Does this element overlap another in the source text?"""

        if isinstance(other, Element):
            other_start, other_end = other.get_range()
        elif type(other) == tuple:
            other_start, other_end = other
        else:
            raise Exception("Can't determine overlap for argument of type {}".format(type(what)))

        if self.start < other.start:
            return self.end > other.start
        elif self.start == other.start:
            return True
        elif self.start > other.start:
            return other.end > self.start

    def normalize_whitespace(self, s):
        s = s.strip()
        s = re.sub(r' +', ' ', s)
        return s

    def __eq__(self, other):
        # Comparing class implies multiple elements can share exactly the same
        # offsets in source text, but only one of each class - that makes sense, I think.
        return isinstance(other, self.__class__) \
            and self.start == other.start \
            and self.end == other.end


class ParsingFailedElement(Element):
    """"""
    def __init__(self, offset, e):
        self.offset = offset
        self.e = e

    def __repr__(self):
        return "ParsingFailedElement(offset={}, e='{}')".format(self.offset, self.e)

