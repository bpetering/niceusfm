# -*- coding: UTF-8 -*-                                                                                            

import sys 
from os.path import dirname
sys.path.append(dirname(dirname(sys.path[0])))

from usfmparser.Parser import Parser

from usfmparser.Elements.Text import Text
from usfmparser.Elements.Whitespace import Whitespace
from usfmparser.Elements.MarkerElement import MarkerElement
from usfmparser.Elements.TextElement import TextElement
from usfmparser.Elements.ParentElement import ParentElement

from usfmparser.Elements.ParagraphMarkerElements import (
    ID, IDE, H, TOC, MT, MS,
    S, SP, P, M, PI, MI, NB, PC, B, P,
    Q, LI,
    ParagraphMarkerElement,
    PARAGRAPH_MARKER_ELEMENTS
)
from usfmparser.Elements.CharacterMarkerElements import (
    W, BK, WJ,
    CharacterMarkerElement,
    CHARACTER_MARKER_ELEMENTS
)
from usfmparser.Elements.NoteMarkerElements import (
    F, FE, X, FR, FT,
    NoteMarkerElement,
    NOTE_MARKER_ELEMENTS
)
from usfmparser.Elements.MilestoneMarkerElements import (
    C, V,
    MilestoneMarkerElement,
    PairedMilestoneMarkerElement,
    MILESTONE_MARKER_ELEMENTS
)






n = Parser('\\p something \\v 2 else')
n.parse()
milestone = n.results.get_milestone('v', 2)
assert(isinstance(milestone, V))
after = milestone.find_after()
assert(isinstance(after, Text))
assert(after.get_text() == 'else')
before = milestone.find_before()
assert(isinstance(before, Text))
assert(before.get_text() == 'something')


v = V(0, 0, (), '1')
elems = [
    P(0, 0, 'p', [
        Text(0, 0, (), 'something'),
        v,
        Text(0, 0, (), 'else')
    ])
]

#assert(v.find_after_all().get_text() == 'else')

