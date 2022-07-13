# -*- coding: UTF-8 -*-

from .Element import Element
from .ChildElement import ChildElement
from ..Exceptions import InvalidElementError

class Text(Element, ChildElement):
    """Class for Text elements. No children - only contains text."""

    def __init__(self, start, end, parents=(), text=''):
        Element.__init__(self, start, end)
        ChildElement.__init__(self, parents)

        self.text = text


    def get_parsed(self, **kwargs):
        return self.text

    def get_text(self, **kwargs):
        # We can't just return self.text.strip(), because 
        # of whitespace preservation rules.
        return self.text

    def value_for_output(self, value):
        value = value.replace('\\', '\\\\')
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        value = value.replace('\t', '\\t')
        return value

    def __repr__(self):
        out = "{}{}(start={}, end={}".format(
            '    ' * self._depth,
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

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
            and self.start == other.start \
            and self.end == other.end \
            and self.parents == other.parents \
            and self.text == other.text

