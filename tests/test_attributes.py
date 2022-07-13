# -*- coding: UTF-8 -*-                                                                                            
# Test parsing of attributes (parsing is separate to Parser)

import sys
from os.path import dirname
sys.path.append(dirname(dirname(sys.path[0])))



import collections

from usfmparser.Exceptions import ParserException, InvalidAttributeException
from usfmparser.Elements.CharacterMarkerElements import W, RB, FIG
from usfmparser.Elements.NoteMarkerElements import XT
from usfmparser.Elements.MarkerElement import MarkerElement
from usfmparser.Elements.SpanMarkerElement import SpanMarkerElement


OD = collections.OrderedDict

### W

w = W(0, 0, (), (MarkerElement(0, 0, (), (), 'null')))
a = w.parse_attributes('|grace')
assert(a)
assert(a == OD([('lemma', 'grace')]))

a = w.parse_attributes('|lemma="grace"')
assert(a)
assert(a == OD([('lemma', 'grace')]))

a = w.parse_attributes('lemma="grace"')
assert(a)
assert(a == OD([('lemma', 'grace')]))

a = w.parse_attributes('|strong="H1234"')
assert(a)
assert(a == OD([('strong', 'H1234')]))

a = w.parse_attributes('strong="H1234"')
assert(a)
assert(a == OD([('strong', 'H1234')]))

a = w.parse_attributes('strong="H1234, G5678"')
assert(a)
assert(a == OD([('strong', ['H1234', 'G5678'])]))



a = w.parse_attributes('lemma="grace" strong="G1234"')
assert(a)
assert(a == OD([('lemma', 'grace'), ('strong', 'G1234')]))

a = w.parse_attributes('|grace strong="G1234"')
assert(a)
assert(a == OD([('lemma', 'grace'), ('strong', 'G1234')]))

a = w.parse_attributes('grace strong="G1234"')
assert(a)
assert(a == OD([('lemma', 'grace'), ('strong', 'G1234')]))

a = w.parse_attributes('strong="G1234" grace')
assert(a)
assert(a == OD([('strong', 'G1234'), ('lemma', 'grace')]))

### TODO
