# -*- coding: UTF-8 -*-

from .MarkerElement import MarkerElement
from .ParentElement import ParentElement
from .NumberedElement import NumberedElement
from .Text import Text
from ..Exceptions import ParserError

# NOTE that specifically the end position of paragraph marker Elements is not the end of the 
# paragraph marker (e.g. '\\p ', it's the end of the entire paragraph


class ParagraphMarkerElement(MarkerElement, ParentElement):
    """Class for Paragraph type markers."""

    def __init__(self, start=None, end=None, marker=None, marker_raw=None, children=()):
        MarkerElement.__init__(self, start, end, marker, marker_raw)
        ParentElement.__init__(self, children)
        self._repr_children = True

    def get_value(self, **kwargs):
        """Some Paragraph type markers have required/optional text following. If so,
           the 'value' is the following text, stripped. Method overridden and raises exception
           if paragraph marker doesn't allow following text (e.g. \\b). The value differs from
           the text in that text can round-trip to recreate parser input, since it preserves
           whitespace and correct text offsets, whereas the value is cleaned of surrounding whitespace."""

        if hasattr(self, 'value'):
            # If value is set explicitly, it's had conversion to another type - use that
            return self.value
        else:
            return self.get_text().replace('  ', ' ').strip()


    def _accumulate_text(self, children, **kwargs):
        ret = ''
        for child in self.children:
            if isinstance(child, F) or isinstance(child, FE):
                if 'include_notes' in kwargs:
                    if kwargs['include_notes']:
                        ret += child.get_text()
                else:
                    ret += child.get_text()
            if isinstance(child, X):
                if 'include_crossref' in kwargs:
                    if kwargs['include_crossref']:
                        ret += child.get_text()
                else:
                    ret += child.get_text()
            if isinstance(child, V) or isinstance(child, C):
                continue
             



    def get_text(self, element_matcher=None, **kwargs):
        # TODO
        # Include any whitespace in self
        ret = self.marker_raw[-1]
        ret += ''.join([x.get_text() for x in self.children])
        return ret

    # TODO get_text_raw() impl that doesn't double spaces
        

    # Somehow, \fig is a paragraph element, with character semantics
    def __instancecheck__(cls, instance):
        # TODO
        n = 0

    def __repr__(self):
        out = "{}{}(start={}, end={}, marker='{}'".format(
            '    ' * self._depth,
            self.__class__.__name__,
            self.start, 
            self.end,
            self.marker
        )   
        if self.children and self._repr_children:
            out += ", children=[\n"
            for child in self.children:
                out += str(child) + ',\n'
            out += '    ' * self._depth + '])'
        else:
            out += ')'
        return out         


# TODO copyright - UBS github.com/ubsicap/usfm


###
# Identification
###

class ID(ParagraphMarkerElement):
    """"""
    
    default_marker = 'id'
    requires_following = True

    def get_code(self):
        tmp = self.get_value()
        code, text = tmp.split(' ', 1)
        return code

    def get_after_code(self):
        tmp = self.get_value()
        code, text = tmp.split(' ', 1)
        return text

    @classmethod
    def parse(cls, thing):
        if not isinstance(thing, str):
            raise ParserError("ID.parse() parses strings")
        if not thing.startswith('\\' + cls.default_marker + ' '):
            raise ParserError("invalid ID")
        tmp = thing[len(cls.default_marker)+2:]
        try:
            code, text = tmp.split(' ', 1)
        except ValueError:
            raise ParserError("Missing CODE / ID text - need both")
        if len(code) != 3:
            raise ParserError("code length wrong")
        # Set start/end None if parsing a specific element
        return ID(cls.default_marker, code=code, text=text)


class USFM(ParagraphMarkerElement):
    """USFM"""

    default_marker = 'usfm'
    requires_following = True


class IDE(ParagraphMarkerElement):
    """IDE"""

    default_marker = 'ide'
    requires_following = True


class H(ParagraphMarkerElement):
    """H"""

    default_marker = 'h'
    requires_following = True


# Inherit from NumberedElement first since it has the correct repr()
class TOC(NumberedElement, ParagraphMarkerElement):
   """TOC"""

   default_marker = 'toc'
   requires_following = True

   def __init__(self, *args, **kwargs):      # TODO ?
        ParagraphMarkerElement.__init__(self, *args)
        NumberedElement.__init__(self, **kwargs)

###
# Introductions
###
class IP(ParagraphMarkerElement):
    """IP"""

    default_marker = 'ip'
    requires_following = True



class IS(ParagraphMarkerElement):

    default_marker = 'is'
    requires_following = True


###
# Titles, Headings, Labels
###

class MT(NumberedElement, ParagraphMarkerElement):
    """MT"""

    default_marker = 'mt'
    requires_following = True

    def __init__(self, *args, **kwargs):      # TODO ?
        ParagraphMarkerElement.__init__(self, *args)
        NumberedElement.__init__(self, **kwargs)


class MS(NumberedElement, ParagraphMarkerElement):
    """MS"""

    default_marker = 'ms'
    requires_following = True

    def __init__(self, *args, **kwargs):      # TODO ?
        ParagraphMarkerElement.__init__(self, *args)
        NumberedElement.__init__(self, **kwargs)


class S(NumberedElement, ParagraphMarkerElement):
    """S"""

    default_marker = 's'
    requires_following = True

    def __init__(self, *args, **kwargs):      # TODO ?
        ParagraphMarkerElement.__init__(self, *args)
        NumberedElement.__init__(self, **kwargs)
        

class D(ParagraphMarkerElement):
    """D"""

    default_marker = 'd'


class SP(ParagraphMarkerElement):
    """SP"""

    default_marker = 'sp'
    requires_following = True


###
# Chapters, Verses
###

# Even though type = 'paragraph', C is parsed as a standalone milestone

class CL(ParagraphMarkerElement):
    """CL"""

    default_marker = 'cl'


class CP(ParagraphMarkerElement):
    """CP"""

    default_marker = 'cp'



### 
# Paragraphs 
### 

class P(ParagraphMarkerElement):
    """P"""

    default_marker = 'p'


class M(ParagraphMarkerElement):
    """M"""

    default_marker = 'm'


class PI(ParagraphMarkerElement):
    """PI"""

    default_marker = 'pi'
    requires_following = True

    def __init__(self, *args, **kwargs):      # TODO ?
        ParagraphMarkerElement.__init__(self, *args)
        NumberedElement.__init__(self, **kwargs)


class MI(ParagraphMarkerElement):
    """MI"""

    default_marker = 'mi'


class NB(ParagraphMarkerElement):
    """NB"""

    default_marker = 'nb'

    def get_value(self):
        return '\n'  # TODO

    def get_text(self):
        return self.get_value()

    def get_text_raw(self):
        return self.marker_raw


class PC(ParagraphMarkerElement):
    """PC"""

    default_marker = 'pc'


class B(ParagraphMarkerElement):
    """B"""

    default_marker = 'b'

    def get_value(self):
        return '\n'

    def get_text(self):
        return self.get_value()

    def get_text_raw(self):
        return self.marker_raw

###
# Poetry
### 

class Q(NumberedElement, ParagraphMarkerElement):
    """Q"""

    default_marker = 'q'
    requires_following = True

    def __init__(self, *args, **kwargs):      # TODO ?
        ParagraphMarkerElement.__init__(self, *args)
        NumberedElement.__init__(self, **kwargs)

###
# Lists
### 
class LI(NumberedElement, ParagraphMarkerElement):
    """LI"""

    default_marker = 'li'
    requires_following = True

    def __init__(self, *args, **kwargs):      # TODO ?
        ParagraphMarkerElement.__init__(self, *args)
        NumberedElement.__init__(self, **kwargs)


# Create mapping marker text => class
PARAGRAPH_MARKER_ELEMENTS = {}
NUMBERED_PARAGRAPH_MARKER_ELEMENTS = {}

v = dict(vars())

for var in v.values():
    if var.__class__ == type:
        if issubclass(var, ParagraphMarkerElement) and var != ParagraphMarkerElement:
            PARAGRAPH_MARKER_ELEMENTS[var.default_marker] = var 
            if issubclass(var, NumberedElement):
                NUMBERED_PARAGRAPH_MARKER_ELEMENTS[var.default_marker] = var

