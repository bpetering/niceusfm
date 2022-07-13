# -*- coding: UTF-8 -*-
# don't circular import in Matchers.py

from .Elements.Element import Element
from .Elements.ParentElement import ParentElement
from .Elements.ChildElement import ChildElement

from .Elements.MarkerElement import MarkerElement
from .Elements.NumberedElement import NumberedElement
from .Elements.SpanMarkerElement import SpanMarkerElement

from .Elements.Text import Text
from .Elements.Whitespace import Whitespace

from .Elements.ConvertableElements import IntConvertableElement, IntRangeConvertableElement

from .Elements.ParagraphMarkerElements import (
    ParagraphMarkerElement,
    PARAGRAPH_MARKER_ELEMENTS,
)
from .Elements.CharacterMarkerElements import (
    CharacterMarkerElement,
    CHARACTER_MARKER_ELEMENTS,
)
from .Elements.NoteMarkerElements import (
    NoteMarkerElement,
    NOTE_MARKER_ELEMENTS,
)
from .Elements.MilestoneMarkerElements import (
    MilestoneMarkerElement,
    PairedMilestoneMarkerElement,
    MILESTONE_MARKER_ELEMENTS,
)

ec_d = {}

for _, add_class in PARAGRAPH_MARKER_ELEMENTS.items():
    ec_d[add_class.__name__] = add_class
for _, add_class in CHARACTER_MARKER_ELEMENTS.items():
    ec_d[add_class.__name__] = add_class
for _, add_class in NOTE_MARKER_ELEMENTS.items():
    ec_d[add_class.__name__] = add_class
for _, add_class in MILESTONE_MARKER_ELEMENTS.items():
    ec_d[add_class.__name__] = add_class
# Include additional parent classes, ...
ec_d[ParentElement.__name__] = ParentElement
ec_d[ChildElement.__name__] = ChildElement
ec_d[NumberedElement.__name__] = NumberedElement
ec_d[ParagraphMarkerElement.__name__] = ParagraphMarkerElement
ec_d[CharacterMarkerElement.__name__] = CharacterMarkerElement
ec_d[NoteMarkerElement.__name__] = NoteMarkerElement
ec_d[SpanMarkerElement.__name__] = SpanMarkerElement
ec_d[MarkerElement.__name__] = MarkerElement
ec_d[Whitespace.__name__] = Whitespace
ec_d[Text.__name__] = Text
ec_d[IntConvertableElement.__name__] = IntConvertableElement
ec_d[IntRangeConvertableElement.__name__] = IntRangeConvertableElement
ec_d[MilestoneMarkerElement.__name__] = MilestoneMarkerElement
ec_d[PairedMilestoneMarkerElement.__name__] = PairedMilestoneMarkerElement

ElementClass = type('ElementClass', (), ec_d)

