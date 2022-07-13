# -*- coding: UTF-8 -*-

from .Element import Element

class MarkerElement(Element):
    """Base class for marker elements. This include milestone markers (which can
       have neither parents nor children), and e.g. Paragraph elements, which can
       have Text and Character/Note children, but no parents, and e.g. F markers,
       which have Paragraph parents and e.g. FR/FT children."""

    def __init__(self, start=None, end=None, marker=None, marker_raw=None, *args, **kwargs):
        Element.__init__(self, start, end, *args, **kwargs)
        
        if not marker:
            self.marker = self.default_marker
        else:
            self.marker = marker

        if marker_raw:
            self.marker_raw = marker_raw

    def get_marker(self):
        return self.marker

    def get_marker_raw(self):
        return self.marker_raw

    def get_text(self):
        return self.marker_raw[-1]

    # TODO def get_text_raw(self):

    # We have .find(), .find_all() on Element. If there's children, those search the children,
    # if they're called on a marker, operates on whatever is indicated by what's enclosed by
    # the marker (searching forwards for start markers and backwards for end markers),
    # Additionally, standalone milestones allow find_next(), find_next_all(), to search
    # forward from that marker until the next identical standalone marker, or until=,
    # to search forward until the same marker (either starting, ending, or standalone). Similarly,
    # find_prev() does the same thing going backwards.


    # We process \c and \v as standalone marker elements.

    # We also provide 'in' operations on marker elements - both start/end with the obvious semantics,
    # and standalone with find_next() semantics (e.g.
    # 'something' in Chapter(3) == Chapter(3).find_next(text_contains='something' or text_eq='something'
    # re.search(r'something', Chapter(3)) == Chapter(3).find_next(text_matches=r'something')
    
    def __eq__(self, other):
        return isinstance(other, self.__class__) \
            and self.start == other.start \
            and self.end == other.end \
            and self.marker == other.marker
    
