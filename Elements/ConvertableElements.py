# -*- coding: UTF-8 -*-

from ..Exceptions import ParserError
from .Text import Text

class VerseNumberSequence:
    """Contiguous verse number sequence"""

    def __init__(self, first_verse, last_verse=None):
        assert(isinstance(first_verse, int))
        if last_verse != None:
            assert(isinstance(last_verse, int))
        self.first_verse = first_verse
        self.last_verse = last_verse

    def __hash__(self):
        return hash((self.first_verse, self.last_verse))

    def __contains__(self, value):
        if self.last_verse == None:
            return value == self.first_verse
        else:
            return value >= self.first_verse and value <= self.last_verse

    def __iter__(self):
        self._iter_idx = 0
        if self.last_verse == None:
            self._iter_values = [self.first_verse]
        else:
            self._iter_values = list(range(self.first_verse, self.last_verse+1))
        return self

    def __next__(self):
        if self._iter_idx == len(self._iter_values):
            raise StopIteration()
        ret = self._iter_values[self._iter_idx]
        self._iter_idx += 1
        return ret

    def __eq__(self, other):
        if isinstance(other, int) and self.last_verse == None:
            return other == self.first_verse
        if isinstance(other, self.__class__):
            return self.first_verse == other.first_verse \
            and self.last_verse == other.last_verse
        return False

    def __ne__(self, other):
        if isinstance(other, int) and self.last_verse == None:
            return other != self.first_verse
        if isinstance(other, self.__class__):
            return self.first_verse != other.first_verse \
            or self.last_verse != other.last_verse
        return True

    def __lt__(self, other):
        if isinstance(other, int):
            return self.first_verse < other
        elif isinstance(other, self.__class__):
            return self.first_verse < other.first_verse
        else:
            raise TypeError("Compare {} against {}".format(other.__class__.__name__))

    def __le__(self, other):
        """"""

    def __gt__(self, other):
        if isinstance(other, int):
            return self.first_verse > other
        elif isinstance(other, self.__class__):
            return self.first_verse > other.first_verse
        else:
            raise TypeError("Compare {} against {}".format(other.__class__.__name__))

    def __ge__(self, other):
        """"""

    def __len__(self):
        if self.last_verse == None:
            return 1
        else:
            return 1 + self.last_verse - self.first_verse

    def __repr__(self):
        if self.last_verse == None:
            return str(self.first_verse)
        else:
            return '{}({}, {})'.format(self.__class__.__name__, self.first_verse, self.last_verse)

    def __str__(self):
        if self.last_verse == None:
            return str(self.first_verse)
        else:
            return '{}-{}'.format(self.first_verse, self.last_verse)


class MultiVerseNumber:
    """More than one VerseNumberSequence, non-contiguous"""


class IntConvertableElement:

    @staticmethod
    def convert(value):
        if isinstance(value, int):
            return int(value)
        if isinstance(value, str):
            try:
                tmp = int(value)
            except TypeError:
                raise ParserError("can't convert {} to int".format(value))
            return tmp
        if isinstance(value, Text):
            text = value.get_text()
            try:
                tmp = int(text)
            except TypeError:
                raise ParserError("can't convert {} to int".format(text))
            return tmp
        raise ParserError("can't convert: {} {}".format(type(value), value))

    @staticmethod
    def validate(value):
        if not isinstance(value, int):
            raise ParserError("Bad type for IntConvertableElement: {} {}".format(type(value), value))
        if value < 1:
            raise ParserError("Bad int value: {}".format(value))




class VerseNumberSequenceConvertableElement:

    @staticmethod
    def convert(value):
        if isinstance(value, str):
            if '-' not in value:
                try:
                    tmp = int(value)
                except TypeError:
                    raise ParserError("Can't convert {} to int".format(value))
                return VerseNumberSequence(tmp)
            else:
                try:
                    parts = [int(x.strip()) for x in value.split('-')]
                except TypeError:
                    raise ParserError("Can't convert to verse range: {}".format(value))
                return VerseNumberSequence(parts[0], parts[1])
        elif isinstance(value, int):
            return VerseNumberSequence(value)
        elif isinstance(value, range):
            if value.step != 1:
                raise TypeError("Conversion from range with .step != 1 is not supported")
            return VerseNumberSequence(value.start, value.stop-1)
        elif isinstance(value, VerseNumberSequence):
            return value
        else:
            raise ParserError("Can't convert {} to {}".format(value, VerseNumberSequence))

    @staticmethod
    def validate(value):
        if not isinstance(value, VerseNumberSequence):
            raise ParserError("VerseNumberSequence validation didn't work: type {} value {}".format(type(value), value))

