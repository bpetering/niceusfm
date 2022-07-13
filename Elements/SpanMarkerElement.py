# -*- coding: UTF-8 -*-

# 'span' = Character or Note markers

import collections
from html.parser import HTMLParser

from .MarkerElement import MarkerElement

from .ParentElement import ParentElement
from .ChildElement import ChildElement
from ..Exceptions import ParserError, InvalidAttributeError


# Markers that are 'character' or 'note' markers (and so can occur in a paragraph), but
# have no matching end marker.
# These all require following text. # \v should not be included.
CHARACTER_NOTE_MARKERS_NO_END = (
        'fr', 'fq', 'fqa', 'fk', 'fl', 'fw', 'fp', 'ft', 
        'xo', 'xk', 'xq', 'xt', 'xta'
)


# Structure is same as HTML, create a fake tag and use HTMLParser!

class USFMHTMLParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        HTMLParser.__init__(self, convert_charrefs=convert_charrefs)
        self.usfm_attrs = []

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] and not attr[1]:
                if attr[0] in ('H', 'G'):
                    raise InvalidAttributeError("'strongs' is not a default attribute")
                self.usfm_attrs.append((self.default_attribute, attr[0]))
            else:
                self.usfm_attrs.append(attr)


class SpanMarkerElement(MarkerElement, ParentElement, ChildElement):
    """Marker elements spanning text. 'end' is required, 
       and this is the first class in the inheritance tree that's allowed to have parents."""

    def __init__(self, start=None, end=None, marker=None, marker_raw=None, parents=(), children=(), attributes=None, attributes_raw=None, end_marker_raw=None):
        MarkerElement.__init__(self, start, end, marker, marker_raw)
        ParentElement.__init__(self, children)
        ChildElement.__init__(self, parents)
        self._repr_children = True

        if attributes:
            if type(attributes) == str:
                self.attributes = self.parse_attributes(attributes)
            else:
                self.attributes = collections.OrderedDict(attributes)
        else:
            self.attributes = collections.OrderedDict()

        if attributes_raw:
            self.attributes_raw = attributes_raw

        if end_marker_raw:
            self.end_marker_raw = end_marker_raw

    def get_value(self):
        # TODO decide about what to return - below
        """The value of span markers is the parse tree of elements in that marker. This differs
           from the value of Paragraph markers, since paragraph markers don't contain other markers
           their value is reduced down to text for convenience."""
        return self.value

    def get_text(self, element_matcher=None, **kwargs):
        # TODO
        # Include any whitespace in self
        ret = self.marker_raw[-1]
        ret += ''.join([x.get_text() for x in self.children])
        return ret    

    def parse_attributes(self, attributes):
        if not isinstance(attributes, str):        #TODO iterable
            raise Exception("attributes must be string")

        if not hasattr(self, 'all_attributes'):
            raise ParserError("{} doesn't have all_attributes".format(self.__class__.__name__))

        attributes = attributes.strip()
        if '|' == attributes[0]:
            attributes = attributes[1:]

        ret = collections.OrderedDict()

        if not hasattr(self, 'default_attribute') and self.default_marker != 'fig':
            raise ParserError("{} does not have a default attribute but it should".format(
                self.__class__.__name__
            ))

        html_parser = USFMHTMLParser()
        html_parser.default_attribute = self.default_attribute
        html_parser.feed('<p ' + attributes + '>')
    
        for attr_tuple in html_parser.usfm_attrs:
            name, value = attr_tuple

            if name not in self.all_attributes and name[:2].lower() != 'x-':
                raise InvalidAttributeError("{} is not a valid attribute for {}".format(
                    name, self.__class__.__name__
                ))

            # TODO non-strict
            # TODO check for srcloc

            if ',' in value and ':' in value:
                raise InvalidAttributeError("{}={} is not valid attribute - mixed , and :".format(
                    name,
                    value
                ))

            if ',' in value:
                value = [x.strip() for x in value.split(',')]
            if ':' in value:
                value = [x.strip() for x in value.split(':')]

            ret[name] = value

        return ret

    

    def __repr__(self):
        out = "{}{}(start={}, end={}, marker='{}'".format(
            '    ' * self._depth,
            self.__class__.__name__,
            self.start,
            self.end,
            self.marker
        )
        if self.attributes:
            out += ", attributes={"
            out += ", ".join(["'" + k + "': '" + self.attributes[k] + "'" for k in self.attributes.keys()])
            out += "}"
        if self.parents:
            out += ", parents=[{}]".format(', '.join([x.marker.upper() for x in self.parents]))
        if self.children and self._repr_children:
            out += ", children=[\n"
            for child in self.children:
                out += str(child) + ',\n'
            out += '    ' * self._depth + '])'
        else:
            out += ')'
        return out
    

    # TODO exclude no children / no attributes


