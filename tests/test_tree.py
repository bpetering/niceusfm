# -*- coding: UTF-8 -*-                                                                                            

import sys 
from os.path import dirname
sys.path.append(dirname(dirname(sys.path[0])))

from usfmparser.Exceptions import (
        ParserException, InvalidMarkerException, NonExistentMarkerException,
        USFMSyntaxErrorException
)

from usfmparser.Parser import Parser, ParserResults
from usfmparser.Token import Token

from usfmparser.Elements.Text import Text
from usfmparser.Elements.Whitespace import Whitespace
from usfmparser.Elements.MarkerElement import MarkerElement
from usfmparser.Elements.TextElement import TextElement
from usfmparser.Elements.TextSpanElement import TextSpanElement
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



p = P(0, 0, 'p', [
        Text(0, 0, (), 'something'),
        W(0, 0, 'w', (), [
                Text(0, 0, (), 'else')
            ],),
        WJ(0, 0, 'wj', (), [
            W(0, 0, 'w', (), [
                Text(0, 0, (), 'more'),
                ]),
            W(0, 0, 'w', (), [
                Text(0, 0, (), 'words'),
                ]),
            ]),
        ])
print(p.flatten())
