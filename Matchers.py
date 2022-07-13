# -*- coding: UTF-8 -*-

import re

from .Elements.Element import Element

class ElementMatcher:
    """ElementMatcher instances specify what other Element instances to match when searching or 
       iterating a list of elements. By default (no arguments), ElementMatcher matches all Element 
       subclasses (and Element itself)."""
    def __init__(self, cls=None, marker=None, instance=None, value=None, number=None, text_eq=None, text_contains=None, text_re_search=None, text_re_match=None, logic_func=all, use_issubclass=True):
        self.cls = cls
        self.marker = marker
        self.instance = instance
        self.value = value
        self.number = number
        self.text_eq = text_eq
        self.text_contains = text_contains
        self.text_re_search = text_re_search
        self.text_re_match = text_re_match

        self._logic_func = logic_func
        self._use_issubclass = use_issubclass

    def match(self, other):
        if not isinstance(other, Element):
            return False

        results = []
        if self.cls != None:
            if type(self.cls) in (list, tuple):
                inner = []
                for cls in self.cls:
                    if self._use_issubclass:
                        inner.append(issubclass(other.__class__, cls))
                    else:
                        inner.append(cls == other.__class__)
                results.append(any(inner))
            else:
                if self._use_issubclass:
                    results.append(issubclass(other.__class__, self.cls))
                else:
                    results.append(self.cls == other.__class__)

        if self.marker != None:
            if type(self.marker) in (list, tuple):
                inner = []
                for marker in self.marker:
                    inner.append(marker == other.marker)
                results.append(any(inner))
            else:
                results.append(self.marker == other.marker)
            
        if self.instance != None:
            if type(self.instance) in (list, tuple):
                inner = []
                for instance in self.instance:
                    inner.append(self.instance == other)
                results.append(any(inner))
            else:
                results.append(self.instance == other)

        if self.value != None:
            # a list of integer values is compared with any(),
            # a list of anything else is compared directly
            if type(self.value) in (list, tuple):
                if any(map(lambda x: type(x) != int, self.value)):
                    results.append(self.value == other.value)
                else:
                    inner = []
                    for value in self.value:
                        inner.append(value == other.value)
                    results.append(any(inner))
            else:
                results.append(self.value == other.value)

        if self.number != None:
            if type(self.number) in (list, tuple):
                inner = []
                for number in self.number:
                    inner.append(number == other.number)
                results.append(any(inner))
            else:       
                results.append(self.number == other.number)
        
        if self.text_eq != None or self.text_contains != None \
        or self.text_re_search != None or self.text_re_match != None:
            other_text = other.get_text()

        if self.text_eq != None:
            if type(self.text_eq) in (list, tuple):
                inner = []
                for text_eq in self.text_eq:
                    inner.append(text_eq == other_text)
                results.append(any(inner))
            else:
                results.append(self.text_eq == other_text)

        if self.text_contains != None:
            if type(self.text_contains) in (list, tuple):
                inner = []
                for text_contains in self.text_contains:
                    inner.append(text_contains in other_text)
                results.append(any(inner))
            else:
                results.append(self.text_contains in other_text)

        if self.text_re_search != None:
            if type(self.text_re_search) in (list, tuple):
                inner = []
                for text_re_search in self.text_re_search:
                    inner.append(re.search(text_re_search, other_text))
                results.append(any(inner))
            else:
                results.append(re.search(self.text_re_search, other_text))

        if self.text_re_match != None:
            if type(self.text_re_match) in (list, tuple):
                inner = []
                for text_re_match in self.text_re_match:
                    inner.append(re.match(text_re_match, other_text))
                results.append(any(inner))
            else:
                results.append(re.match(self.text_re_match, other_text))

        return self._logic_func(results)

    def __or__(self, other):
        return ElementMatcherCombined((self, other), any)

    def __and__(self, other):
        return ElementMatcherCombined((self, other), all)



class ElementMatcherCombined(ElementMatcher):
    def __init__(self, matchers=(), logic_func=None):
        if matchers:
            self.matchers = list(matchers)
        if logic_func:
            self.logic_func = logic_func







    def match(self, other):
        results = [x.match(other) for x in self.matchers]
        return self.logic_func(results)

