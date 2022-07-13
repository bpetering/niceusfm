# -*- coding: UTF-8 -*-


import json

from .SpanMarkerElement import SpanMarkerElement

class CharacterMarkerElement(SpanMarkerElement):
    """Character Markers"""

    def get_value(self):
        return ''.join([x.get_text() for x in self.children])

class CharacterMarkerElementEncoder(json.JSONEncoder):
    def default(a, d):


        if isinstance(d, CharacterMarkerElement):
            return { 'class_name': d.__class__.__name__, 'attributes': d.attributes, 'text': d.get_value() }
        else:
            return json.JSONEncoder.default(a, d)







# TODO decoding hierarchies of objects

###
# Chapters, Verses
###

# Even though V is type 'character', it's parsed as a standalone milestone


class CA(CharacterMarkerElement):
    """CA"""

    default_marker = 'ca'


class VA(CharacterMarkerElement):
    """VA"""

    default_marker = 'va'


###
# Words and Characters - Special Features
###

class W(CharacterMarkerElement):
    """W"""

    default_marker = 'w'
    default_attribute = 'lemma'




    all_attributes = ('lemma', 'strong', 'srcloc')

    def __init__(self, start=None, end=None, marker=None, marker_raw=None, parents=(), children=(), attributes=    None, attributes_raw=None, end_marker_raw=None):
        CharacterMarkerElement.__init__(self, start, end, marker, marker_raw, parents, children, attributes, attributes_raw, end_marker_raw)



class RB(CharacterMarkerElement):
    """RB"""

    default_marker = 'rb'
    default_attribute = 'gloss'
    all_attributes = ('gloss')

    def __init__(self, start=None, end=None, marker=None, marker_raw=None, parents=(), children=(), attributes=    None, attributes_raw=None, end_marker_raw=None):
        CharacterMarkerElement.__init__(self, start, end, marker, marker_raw, parents, children, attributes, attributes_raw, end_marker_raw)


class FIG(CharacterMarkerElement):
    """FIG"""
    # type: paragraph, but needs parsing as CharacterMarkerElement.
    # no default attribute.

    default_marker = 'fig'
    required_attributes = ('src', 'size', 'ref')

    
    all_attributes = ('alt', 'src', 'size', 'loc', 'copy', 'ref')

    def __init__(self, start=None, end=None, marker=None, marker_raw=None, parents=(), children=(), attributes=    None, attributes_raw=None, end_marker_raw=None):
        CharacterMarkerElement.__init__(self, start, end, marker, marker_raw, parents, children, attributes, attributes_raw, end_marker_raw)

###
# Poetry
###
class QS(CharacterMarkerElement):
    """QS"""

    default_marker = 'qs'

    

###
# Words and Characters - Special Text
###

class ADD(CharacterMarkerElement):
    """ADD"""

    default_marker = 'add'


class BK(CharacterMarkerElement):
    """BK"""

    default_marker = 'bk'


class DC(CharacterMarkerElement):
    """DC"""

    default_marker = 'dc'


class K(CharacterMarkerElement):
    """K"""

    default_marker = 'k'


class ND(CharacterMarkerElement):
    """ND"""

    default_marker = 'nd'


class ORD(CharacterMarkerElement):
    """ORD"""

    default_marker = 'ord'


class PN(CharacterMarkerElement):
    """PN"""

    default_marker = 'pn'


class PNG(CharacterMarkerElement):
    """PNG"""

    default_marker = 'png'


class QT(CharacterMarkerElement):
    """QT"""

    default_marker = 'qt'


class WJ(CharacterMarkerElement):
    """An element for Words of Jesus"""

    default_marker = 'wj'


    def __init__(self, start=None, end=None, marker=None, marker_raw=None, parents=(), children=(), attributes=    None, attributes_raw=None, end_marker_raw=None):
        CharacterMarkerElement.__init__(self, start, end, marker, marker_raw, parents, children, attributes, attributes_raw, end_marker_raw)


# Create mapping marker text => class
CHARACTER_MARKER_ELEMENTS = {}

v = dict(vars())

for var in v.values():
    if var.__class__ == type:
        if issubclass(var, CharacterMarkerElement) and var != CharacterMarkerElement:
            CHARACTER_MARKER_ELEMENTS[var.default_marker] = var 


