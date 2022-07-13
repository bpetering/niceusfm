# -*- coding: UTF-8 -*-

from .Element import Element

class TextElement(Element):
    """Base class for text elements (not beginning with a marker). Text can contain marker
       elements within it."""

    def __init__(self, start, end, parents=(), children=()):
        Element.__init__(self, start, end, parents)
        self.text = text


    def get_raw(self):
        return self.text

    def get_text(self):
        return self.text

    def value_for_output(self, value):
        value = value.replace('\\', '\\\\')
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        value = value.replace('\t', '\\t')
        return value

    def __repr__(self):
        out = "{}(start={}, end={}".format(
            self.__class__.__name__,
            self.start,
            self.end
        )
        if self.parents:
            out += ", parents=[{}]".format(
                ','.join([x.marker.upper() for x in self.parents]),
            )
        out += ", text='{}')".format(
            self.value_for_output(self.get_text())
        )
        return out
