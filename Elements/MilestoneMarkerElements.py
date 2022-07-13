# -*- coding: UTF-8 -*- 

from .MarkerElement import MarkerElement
from .ConvertableElements import IntConvertableElement, VerseNumberSequenceConvertableElement
from .ChildElement import ChildElement
from .ParentElement import ParentElement
from ..Matchers import ElementMatcher
from ..Exceptions import InvalidMarkerError
from .Text import Text
from .Whitespace import Whitespace
from .NoteMarkerElements import F, FE, X

from .CharacterMarkerElements import W
from .ParagraphMarkerElements import MS, D, SP, Q, D

FORWARD = 1
BACKWARD = 2


# TODO do these need ChildElement?
class MilestoneMarkerElement(MarkerElement, ChildElement):
    """Milestone marker class, including standalone elements. These occur in the parse tree,
       but they're not usable in the same way as tree elements (they're on a different axis)"""


    DEFAULT_TRAVERSE_NUM_ANCESTORS = 5      # TODO customise

    def __init__(self, start=None, end=None, marker=None, marker_raw=None, parents=()):
        MarkerElement.__init__(self, start, end, marker, marker_raw)
        ChildElement.__init__(self, parents)
        self._repr_children = True

    def get_text(self):
        return str(self.value)

    def get_parsed(self, **kwargs):
        # To round-trip, we use marker_raw unless the element has children
        return self.marker_raw

    # does this naming working - nested milestone pairs?

    def elements_from(self, direction=FORWARD, include=None, until=None, first=None, last=None):
        """Get elements, beginning from this marker, traversing either forward 
           (MilestoneMarkerElement.FORWARD) or backward, including elements matched by 
           the ElementMatcher include, until the Element matched by until, returning
           either first N or last N results, not including this marker and until."""
        if first != None and last != None:
            raise ValueError("elements_after() received both 'first' and 'last' arguments")

        if include == None:
            include = ElementMatcher()  # match any Element instance

        if direction == FORWARD:
            all_flattened = self._root.get_flattened_forward()
            if hasattr(self, '_my_forward_idx'):         # assumes unchanging
                my_idx = self._my_forward_idx
            else:
                my_idx = all_flattened.index(self)
                self._my_forward_idx = my_idx
            
        elif direction == BACKWARD:
            all_flattened = self._root.get_flattened_backward()
            if hasattr(self, '_my_backward_idx'):         # assumes unchanging
                my_idx = self._my_backward_idx
            else:
                my_idx = all_flattened.index(self)
                self._my_backward_idx = my_idx

        ret = []
        for elem in all_flattened[my_idx+1:]:
            if until and until.match(elem):
                break
            if include.match(elem):
                ret.append(elem)
        if first != None:
            return ret[:first]
        if last != None:
            return ret[-last:]
        return ret

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
            and self.start == other.start \
            and self.end == other.end \
            and self.marker == other.marker \
            and self.value == other.value

    def __repr__(self):
        if not hasattr(self, '_depth'):
            depth = 1
        else:
            depth = self._depth

        out = "{}{}(start={}, end={}, marker='{}', value={}".format(
            '    ' * depth,
            self.__class__.__name__,
            self.start,
            self.end,
            self.marker,
            self.value
        )   
        if self.parents:
            out += ", parents=[{}]".format(', '.join([x.marker.upper() for x in self.parents]))
        out += ')' 
        return out 




    def __hash__(self):
        return hash((self.start,))


class PairedMilestoneMarkerElement(MilestoneMarkerElement):
    """A milestone marker element that has a matching pair. If a milestone marker isn't paired,
       it's standalone."""

    TYPE_START = 1
    TYPE_END = 2

    def __init__(self, start=None, end=None, marker=None, marker_raw=None, parents=(), milestone_type=None, pair=None):
        # For paired elements, we include marker_raw in each type (start/end) - these are processed differently
        MilestoneMarkerElement.__init__(self, start, end, marker, marker_raw, parents)

        if milestone_type not in (self.TYPE_START, self.TYPE_END):
            raise InvalidMarkerError("Paired milestone needs milestone_type=(.TYPE_START|.TYPE_END), got {}".format(
                milestone_type
            ))

        if pair:
            self.pair = pair

    def get_pair(self):
        return self.pair

    # first_within == start.elements_within(include=include, until=end, first=1)
    # last_within  == 

    def elements_within(self, direction=FORWARD, include=None, until=None, first=None, last=None):
        """"""
        if direction == FORWARD:
            if self.milestone_type == self.TYPE_START:
                start = self
                end = self.get_pair()
            else:
                start = self.get_pair()
                end = self
        elif direction == BACKWARD:
            if self.milestone_type == self.TYPE_START:
                start = self.get_pair()
                end = self
            else:
                start = self
                end = self.get_pair()
        else:
            raise ValueError("Unknown value {} for direction in elements_within()".format(direction))

        if until:
            combined = end & until
        else:
            combined = end
        return start.elements_from(
            direction=direction, 
            include=include, 
            until=combined, 
            first=first, 
            last=last
        )



class C(MilestoneMarkerElement, IntConvertableElement, ParentElement):
    """Marker element representing chapter."""

    default_marker = 'c' 
    requires_following = True       # TODO needed?
    # TODO is instance Paragraph

    def __init__(self, start=None, end=None, marker=None, marker_raw=None, parents=(), children=(), value=None):
        MilestoneMarkerElement.__init__(self, start, end, marker, marker_raw, parents)
        ParentElement.__init__(self, children)
        if value != None:
            self.value = self.convert(value)
            self.validate(self.value)
        else:
            self.value = None

    def get_value(self):
        return self.value


    def get_flattened_forward(self):
        if hasattr(self, '_flattened_forward'):
            return self._flattened_forward
        else:
            self._repr_children = False
            flattened_forward = [self]



            # No children included when flattening
            self._flattened_forward = flattened_forward
            return flattened_forward






    def get_verse(self, verse):
        assert(isinstance(verse, int))

        for c in self.children:
            if isinstance(c, V):
                if c.value == verse:
                    return c
        return None

    def get_verses(self):

        ret = []
        for c in self.children:
            if isinstance(c, V):
                ret.append(c)



        return ret

    def get_first_text(self):
        """Return text between the \\c and \\v 1 (first verse) markers"""
        m1 = ElementMatcher(cls=Text)
        m2 = ElementMatcher(cls=Whitespace)

        no_ancestor_include = ElementMatcher(cls=F)
        no_ancestor_include |= ElementMatcher(cls=FE)
        no_ancestor_include |= ElementMatcher(cls=X)
        no_ancestor_include |= ElementMatcher(cls=MS)

        first_text = ''.join([
            # confusing - from flattened/hierarchy
            x.get_text() for x in self.elements_from(include=m1|m2, until=ElementMatcher(cls=V)) if not x.has_ancestor(include=no_ancestor_include)
        ])
        return self.normalize_whitespace(first_text)




        return ret

    def get_text(self):
        # Include a previous \d TODO ?

        m1 = ElementMatcher(cls=Text)
        m2 = ElementMatcher(cls=Whitespace)

        no_ancestor_include = ElementMatcher(cls=F)
        no_ancestor_include |= ElementMatcher(cls=FE)
        no_ancestor_include |= ElementMatcher(cls=X)



        chapter_text = ''.join([
            # confusing - from flattened/hierarchy
            x.get_text() for x in self.elements_from(include=m1|m2, until=ElementMatcher(cls=C)) if not x.has_ancestor(include=no_ancestor_include)
        ])
        return self.normalize_whitespace(chapter_text)

    def __repr__(self):
        if not hasattr(self, '_depth'):
            depth = 1
        else:
            depth = self._depth

        out = "{}{}(start={}, end={}, marker='{}', value={}".format(
            '    ' * depth,
            self.__class__.__name__,
            self.start,
            self.end,
            self.marker,
            self.value
        )   

        if self.parents:
            out += ", parents=[{}]".format(', '.join([x.marker.upper() for x in self.parents]))

        if self.children and self._repr_children:
            out += ", children=[\n"
            for child in self.children:
                out += "{}{}(start={}, end={}, marker='{}', parents=[C], value={}),\n".format(
                    '    ' * (depth+1), child.__class__.__name__, 
                    child.start, child.end, child.marker, child.value
                )
            out += '    ' * depth 
            out + "])"
        else:
            out += ')' 
        return out 




Chapter = C 



class V(MilestoneMarkerElement, VerseNumberSequenceConvertableElement):
    """V"""

    default_marker = 'v'
    requires_following = True
    # TODO isinstance character

    # This has 2 parents: 1 for chapter marker, 1 for logical parent in text

    def __init__(self, start=None, end=None, marker=None, marker_raw=None, parents=(), value=None):
        MilestoneMarkerElement.__init__(self, start, end, marker, marker_raw, parents)

        if value != None:
            self.value = self.convert(value)
            self.validate(self.value)
        else:
            self.value = None

    #def get_text(self, **kwargs):
    #    ret = self.marker_raw[-1]
    #    return ret + str(self.value)

    def get_value(self):
        return self.value
    

    # TODO flattened / elements_from API -confusing. (flattening - mistake)


    def get_words(self):





        m1 = ElementMatcher(cls=W)
        m2 = ElementMatcher(cls=C) | ElementMatcher(cls=V)

        no_ancestor_include = ElementMatcher(cls=F)
        no_ancestor_include |= ElementMatcher(cls=FE)
        no_ancestor_include |= ElementMatcher(cls=X)
        no_ancestor_include |= ElementMatcher(cls=SP)



        return [x for x in self.elements_from(include=m1, until=m2|ElementMatcher(cls=D)) if not x.has_ancestor(include=no_ancestor_include) and not getattr(x, '_psalm_119_skip', False)]


    def get_text(self):

        m1 = ElementMatcher(cls=Text) | ElementMatcher(cls=Whitespace)


        m2 = ElementMatcher(cls=C) | ElementMatcher(cls=V)

        no_ancestor_include = ElementMatcher(cls=F)
        no_ancestor_include |= ElementMatcher(cls=FE)
        no_ancestor_include |= ElementMatcher(cls=X)
        no_ancestor_include |= ElementMatcher(cls=SP)

        verse_text = ''.join([
            # confusing - from flattened/hierarchy
            x.get_text() for x in self.elements_from(include=m1, until=m2|ElementMatcher(cls=D)) if not x.has_ancestor(include=no_ancestor_include) and not getattr(x, '_psalm_119_skip', False)
        ])

        return self.normalize_whitespace(verse_text)




    def __repr__(self):
        if not hasattr(self, '_depth'):
            depth = 1
        else:
            depth = self._depth

        out = "{}{}(start={}, end={}, marker='{}', value={}".format(
            '    ' * depth,
            self.__class__.__name__,
            self.start,
            self.end,
            self.marker,
            self.value
        )   

        if self.parents:
            out += ', parents=['
            p_out = ''
            for p in self.parents:
                if p_out:
                    p_out += ', '
                value = getattr(p, 'value', '')
                if value:
                    p_out += p.marker.upper() + '.' + str(value)
                else:
                    p_out += p.marker.upper()
            out += p_out
            out += ']'
                
        out += ')' 

        return out 

Verse = V




# Create mapping marker text => class
MILESTONE_MARKER_ELEMENTS = {}
        
v = dict(vars())
        
for var in v.values():
    if var.__class__ == type:
        if issubclass(var, MilestoneMarkerElement) \
        and var not in (MilestoneMarkerElement, PairedMilestoneMarkerElement):
            MILESTONE_MARKER_ELEMENTS[var.default_marker] = var

# Create Paired elements for all Character markers except V.
# TODO

