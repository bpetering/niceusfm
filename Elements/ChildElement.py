# -*- coding: UTF-8 -*-                                                                                            
from .Element import Element
from ..Matchers import ElementMatcher

class ChildElement:
    """A child element has parents. Base class for elements that are contained within other elements."""
    # TODO gc circular refs
    def __init__(self, parents=(), *args, **kwargs):
        if isinstance(parents, Element):
            self.parents = [parents]
        elif type(parents) in (list, tuple):
            self.parents = list(parents)
        elif not parents:
            self.parents = []
        else:
            raise Exception("parents - type {} value {}".format(type(parents), parents))

        for k in kwargs:
            if kwargs[k]:
                setattr(self, k, kwargs[k])
    
    def find_above(self, cls=None, value=None, marker=None, text_eq=None, text_contains=None, text_matches=None):
        """Find and return the **first** Element with all specified class, marker, value, and text, from
           this element and higher in the tree. Return the Element or None."""

    def find_above_all(self, cls=None, value=None, marker=None, text_eq=None, text_contains=None, text_matches=None):
        """Find and return the **first** Element with all specified class, marker, value, and text, from
           this element and higher in the tree. Return the Element or None."""
    
    def has_ancestor(self, include=None, until=None):
        if not include:
            include = ElementMatcher()
        
        if not self.parents:
            return False

        parent = self.parents[0]
        if until and until.match(parent):
            return False
        if include.match(parent):
            return True

        parents = getattr(parent, 'parents', None)
        while parents:
            parent = parents[0]     # TODO which path to choose?
            if until and until.match(parent):
                return False
            if include.match(parent):
                return True
            parents = getattr(parent, 'parents', None)

        return False
