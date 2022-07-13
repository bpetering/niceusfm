# -*- coding: UTF-8 -*-

from .SpanMarkerElement import SpanMarkerElement

class NoteMarkerElement(SpanMarkerElement):
    """Note Markers"""


###
# Footnotes
###

class F(NoteMarkerElement):
    """F"""

    default_marker = 'f'


class FE(NoteMarkerElement):
    """FE"""

    default_marker = 'fe'


class FR(NoteMarkerElement):
    """FR"""

    default_marker = 'fr'

class FQ(NoteMarkerElement):

    default_marker = 'fq'


class FQA(NoteMarkerElement):

    default_marker = 'fqa'


class FK(NoteMarkerElement):
    """FK"""

    default_marker = 'fk'


class FL(NoteMarkerElement):
    """FL"""

    default_marker = 'fl'


class FW(NoteMarkerElement):
    """FW"""

    default_marker = 'fw'


class FP(NoteMarkerElement):
    """FP"""

    default_marker = 'fp'


class FV(NoteMarkerElement):
    """FV"""

    default_marker = 'fv'
   

class FT(NoteMarkerElement):
    """FT"""

    default_marker = 'ft'
    requires_following = True


class FDC(NoteMarkerElement):
    """FDC"""

    default_marker = 'fdc'


class FM(NoteMarkerElement):
    """FM"""

    default_marker = 'fm'


FOOTNOTE_MARKERS = ('f', 'fe', 'fr', 'fk', 'fl', 'fw', 'fp', 'fv', 'ft', 'fdc', 'fm')


###
# Cross References
###

class X(NoteMarkerElement):
    """X"""

    default_marker = 'x'


class XO(NoteMarkerElement):
    """XO"""

    default_marker = 'xo'


class XQ(NoteMarkerElement):
    """XQ"""

    default_marker = 'xq'


class XOP(NoteMarkerElement):
    """XOP"""

    default_marker = 'xop'


class XT(NoteMarkerElement):
    """XT"""

    default_marker = 'xt'
    default_attribute = 'link-href'

    def __init__(self, start=None, end=None, marker=None, marker_raw=None, parents=(), children=(), attributes=    None, attributes_raw=None, end_marker_raw=None):
        NoteMarkerElement.__init__(self, start, end, marker, marker_raw, parents, children, attributes, attributes_raw, end_marker_raw)
    


CROSS_REFERENCE_MARKERS = ('x', 'xo', 'xq', 'xop', 'xt')



# Create mapping marker text => class
NOTE_MARKER_ELEMENTS = {}
FOOTNOTE_MARKER_ELEMENTS = {}
CROSS_REFERENCE_MARKER_ELEMENTS = {}

v = dict(vars())

for var in v.values():
    if var.__class__ == type:
        if issubclass(var, NoteMarkerElement) and var != NoteMarkerElement:
            NOTE_MARKER_ELEMENTS[var.default_marker] = var 
            if var.default_marker in FOOTNOTE_MARKERS:
                FOOTNOTE_MARKER_ELEMENTS[var.default_marker] = var
            if var.default_marker in CROSS_REFERENCE_MARKERS:
                CROSS_REFERENCE_MARKER_ELEMENTS[var.default_marker] = var
            

