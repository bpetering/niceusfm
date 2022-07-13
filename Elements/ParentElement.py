# -*- coding: UTF-8 -*-                                                                                            
import re

from .Element import Element
from ..Matchers import ElementMatcher


class ParentElement:
    """A parent element has children. Base class for elements that can contain other elements (children)."""

    def __init__(self, children=()):
        if isinstance(children, Element):
            self.children = [children]
        elif type(children) in (list, tuple):
            self.children = list(children)          # TODO append - clear flattened
        elif not children:
            self.children = []
        else:
            raise Exception("children - type {} value {}".format(type(children), children))

    #def __repr__(self):
    #    out = '\t' * self.children_level + '[\n'
    #    for child in self.children:
    #        out += '\t' * (self.children_level + 1) + Element.__repr__(child)
    #    out += '\t' * self.children_level + ']\n'
    #    return out

    # get_text* in specific classes

    def get_flattened(self):
        """Return all child Elements, recursively, in a flattened list"""
        return self.get_flattened_forward()

    def get_flattened_forward(self):
        if hasattr(self, '_flattened_forward'):
            return self._flattened_forward
        else:
            self._repr_children = False
            flattened_forward = [self]
            flattened_forward.extend(self._get_flattened_forward(self.children))
            self._flattened_forward = flattened_forward
            return flattened_forward

    def get_flattened_backward(self):
        if hasattr(self, '_flattened_backward'):
            return self._flattened_backward
        else:
            backward = list(self.get_flattened_forward())
            backward.reverse()
            self._flattened_backward = backward
            return backward

    def _get_flattened_forward(self, elems):
        all_elems = []
        for e in elems:
            if isinstance(e, ParentElement):
                all_elems.extend(e.get_flattened_forward())
            else:
                all_elems.append(e)
        return all_elems

    def __iter__(self):
        self._flattened_forward_idx = 0
        return self

    def __next__(self):
        if not hasattr(self, '_flattened_forward'):
            self.get_flattened_forward()
        if self._flattened_forward_idx == len(self._flattened_forward):
            raise StopIteration
        elem = self._flattened_forward[self._flattened_forward_idx]
        self.flattened_forward_idx += 1
        return elem

    # TODO don't repr children if empty

    # TODO these methods on parser results

    def find_below(self, element_matcher=None, **kwargs):
        """Find and return the **first** Element with all specified class, marker, value, and text, from
           this element down in the tree. Return the Element or None."""
        if not element_matcher:
            element_matcher = ElementMatcher()

        for elem in self.get_flattened():
            n=0     # TODO need 

    def find_below_all(self, element_matcher=None, **kwargs):
        """Find and return **all** the Elements with all specified class, marker, value, and text, from
           this element down in the tree. Return an iterable of the Elements."""

    def has_descendant(self, element_matcher=None, until=None):
        """Inverse of has_ancestor()."""
    
    # Help view the parse tree
    def __getattr__(self, name):
        if name.startswith('c'):
            m = re.match(r'c(\d+)', name)
            if m:
                return self.children[int(m.group(1))]
        raise AttributeError("{}: attribute {} doesn't exist".format(self.__class__.__name__, name))


