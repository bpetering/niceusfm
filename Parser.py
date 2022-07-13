# -*- coding: UTF-8 -*-
# TODO annotate backtraces with Parser line_num
# TODO include line_num in more exceptions
# TODO include file name in exceptions

import re
import collections

from .Exceptions import (
        ParserError, InvalidMarkerError, 
        NonExistentMarkerError, NoTokenError,
        USFMSyntaxError
)

from .Tokenizer import Tokenizer
from .Token import Token

from .Elements.Element import ParsingFailedElement
from .Elements.Text import Text
from .Elements.Whitespace import Whitespace

from .Matchers import ElementMatcher

from .Elements.ParentElement import ParentElement
from .Elements.SpanMarkerElement import CHARACTER_NOTE_MARKERS_NO_END
from .Elements.NumberedElement import NumberedElement
from .Elements.ConvertableElements import IntConvertableElement, VerseNumberSequence

from .Elements.ParagraphMarkerElements import (
    ID, IDE, H, TOC, MT, MS, 
    S, SP, P, M, PI, MI, NB, PC, B, P,
    Q, LI, 
    D,
    ParagraphMarkerElement,
    PARAGRAPH_MARKER_ELEMENTS
)
from .Elements.CharacterMarkerElements import (
    W, BK, WJ,
    CharacterMarkerElement,
    CHARACTER_MARKER_ELEMENTS
)
from .Elements.NoteMarkerElements import (
    F, FE, X,
    NoteMarkerElement,
    NOTE_MARKER_ELEMENTS
)

from .Elements.MilestoneMarkerElements import (
    C, V,
    MilestoneMarkerElement,
    PairedMilestoneMarkerElement,
    MILESTONE_MARKER_ELEMENTS
)

ALL_EXISTING_MARKERS = {x.default_marker:1 for x in 
    list(PARAGRAPH_MARKER_ELEMENTS.values()) + 
    list(CHARACTER_MARKER_ELEMENTS.values()) +
    list(NOTE_MARKER_ELEMENTS.values())
}


SPAN_MARKERS_PAIR = set(list(CHARACTER_MARKER_ELEMENTS.keys()) + list(NOTE_MARKER_ELEMENTS.keys())) - set(CHARACTER_NOTE_MARKERS_NO_END)


class ParserResults(collections.deque):

    def __init__(self, iterable=None, maxlen=None):
        if iterable == None and maxlen == None:
            collections.deque.__init__(self)
        elif iterable != None and maxlen == None:
            collections.deque.__init__(self, iterable)
        elif iterable != None and maxlen != None:
            collections.deque.__init__(self, iterable, maxlen)

        self.milestones = {}
        self.chapters = {}
    
    # element , int
    def get_chapter(self, chapter):
        assert(isinstance(chapter, int))    
        if chapter in self.chapters:
            return self.chapters[chapter]
        else:
            return None

    def get_verse(self, chapter, verse):
        assert(isinstance(verse, int))
        chapter = self.get_chapter(chapter)
        if not chapter:
            return None
        return chapter.get_verse(verse)

    def get_chapters(self):
        numbers = list(self.chapters.keys())
        if not numbers:
            return []
        numbers.sort()
        ret = []
        for number in numbers:
            ret.append(self.chapters[number])
        return ret

    def get_number_of_chapters(self):
        """"""
        return len(self.chapters.keys())

    def get_number_of_verses(self, chapter):
        """"""
        assert(isinstance(chapter, int))
        chapter = self.get_chapter(chapter)

        return len(chapter.get_verses())

    def get_flattened(self):
        return self.get_flattened_forward()

    def get_flattened_forward(self):
        # ParserResults don't change once parsed, store fwd and backward
        if hasattr(self, '_flattened_forward'):
            return self._flattened_forward

        all_elems = []
        for elem in self:
            if isinstance(elem, ParentElement):
                all_elems.extend(elem.get_flattened_forward())
            else:
                all_elems.append(elem)
        self._flattened_forward = all_elems
        return all_elems

    def get_flattened_backward(self):
        if hasattr(self, '_flattened_backward'):
            return self._flattened_backward
        else:
            backward = list(self.get_flattened_forward())
            backward.reverse()
            self._flattened_backward = backward
            return backward

    def get_chapter_elements(self, chapter):
        """"""
        # TODO P crossing chapter?
        milestone = self.get_chapter_milestone(self, chapter)
        return milestone.elements_from(until=ElementMatcher(cls=C))

    def get_chapter_verse_elements(self, chapter, verse):
        """"""
        chapter_verse_milestone = self.get_chapter_verse_milestone(chapter, verse)
        return chapter_verse_milestone.elements_from(until=ElementMatcher(cls=V))

    # These methods correspond to markers in 'Identification'

    def _get_ident_elems(self, elem_cls, first=1):
        ret = []
        if not self:
            raise AttributeError("get_<ident elem>() can only be called after .parse()")
        for elem in self:
            if isinstance(elem, elem_cls):
                if first == 1:
                    return elem
                else:
                    ret.append(elem)
        if first == 1:
            return None
        return ret[:first]

    def get_id(self):
        return self._get_ident_elems(ID)

    def get_usfm(self):
        return self._get_ident_elems(USFM)

    def get_ide(self):
        return self._get_ident_elems(IDE)

    def get_h(self): 
        return self._get_ident_elems(H)

    def get_toc(self, number=1):
        tocs = self._get_ident_elems(TOC, 20)
        for t in tocs:
            if t.number == number:
                return t
        return None

    def get_toca(self, number=1):
        tocas = self._get_ident_elems(TOCA, 20)
        for t in tocas:
            if t.number == number:
                return t
        return None


    # Help view the parse tree
    def __getattr__(self, name):
        if name.startswith('r'):
            m = re.match(r'^r(\d+)', name)
            if m:
                return self[int(m.group(1))]
        raise AttributeError()

    def __repr__(self):
        out = 'ParserResults([\n'
        for elem in self:
            out += '{}\n'.format(elem)
        out += '])\n'

        return out


class Parser:
    """A USFM Parser class, taking text (incrementally if needed) and TODO yield/return
       of trees of Elements. Provide text to the constructor or incrementally with .add(text).

       Should be able to accept text character-at-a-time (but avoid), line-at-a-time,
       buffer-at-a-time, or file-at-a-time.

       Parsing doesn't happen automatically - parse() must be called."""

    DEFAULT_MAX_DEPTH = 3

    def __init__(self, text='', **kwargs):
        self.tokenizer = Tokenizer()    # discard?
        if text:
            self.tokenizer.add(text)

        # Indices into tokenizer.tokens
        self.parsing_bound = 0          # discard?
        self.try_bound = 0

        self.results = ParserResults()
        self.results.parser = self      # requires reference to use line num
        
        self._last_paired_milestone_markers = {}
        self._current_chapter_marker = None
        self._current_verse_marker = None


        self._prev_d_text = None

        for k in kwargs:
            setattr(self, k, kwargs[k])

        self.DEBUG = 1

        #if self.DEBUG:
        #    self.tokenizer.DEBUG = 1
        #    print('\n\n\nPARSER CONSTRUCT: {}'.format(text))

    def __getattr__(self, name):
        if name.startswith('r'):
            if name == 'r':
                return self.results
            else:
                m = re.match(r'^r(\d+)', name)
                if m:
                    return self.results[int(m.group(1))]
        raise AttributeError()

    def add(self, text):
        self.tokenizer.add(text)
        if self.DEBUG:
            print('\n\n\nPARSER ADD: {}'.format(text))

    def reset(self):
        """Reset entire state of parser"""
        self.tokenizer.reset()
        self.parsing_bound = 0
        self.try_bound = 0
        self.results = ParserResults()

    def get_marker_class(self, marker):
        """Get a marker class from the marker (e.g. 'p')"""
        if marker in PARAGRAPH_MARKER_ELEMENTS:
            return PARAGRAPH_MARKER_ELEMENTS[marker]
        elif marker in CHARACTER_MARKER_ELEMENTS:
            return CHARACTER_MARKER_ELEMENTS[marker]
        elif marker in NOTE_MARKER_ELEMENTS:
            return NOTE_MARKER_ELEMENTS[marker]
        elif marker in MILESTONE_MARKER_ELEMENTS or '-' in marker:
            marker = marker.lower()
            if '-' in marker:
                marker = marker.replace('-s', '').replace('-e', '')
                if marker in MILESTONE_MARKER_ELEMENTS:
                    return MILESTONE_MARKER_ELEMENTS[marker]
                else:
                    raise ParserError("something itsn't working")
            else:
                return MILESTONE_MARKER_ELEMENTS[marker]
        else:
            raise ParserError("[~line {}] Couldn't get marker class for marker={}".format(
                self.line_num, marker
            ))

    def parse(self):
        """Parse using tokens we have so far. If text added doesn't form complete
           tokens, only the complete tokens will be parsed, taking into consideration 
           things like \\h (which needs a following space), or \\c (which needs a following
           space and a number.

           If text added has character or note type markers (e.g. markers that can 'contain' 
           text), parse() won't yield until the closing marker is found, including nesting.

           
           
           'All new character marker starts (without the + prefix) close all existing nesting.'

        """
        self.line_num = 1
        self.tokenizer.tokenize()

        # TODO
        if '\r' in self.tokenizer.text:
            raise ParserError("unsupported newlines")

        if self.DEBUG:
            print(self.tokenizer.tokens)

        self.try_bound = self.parsing_bound

        #if self.DEBUG:
        #    print('nearly main loop, tokens = {}'.format(self.tokenizer.tokens))

        while self.current_token():
            token = self.current_token()
            if self.DEBUG:
                print("MAIN LOOP token = {}".format(token))

            # Text and whitespace. Don't collapse this, because processors are 
            # written in terms of parsers, and processors need to preserve significant whitespace.
            # Whether these can occur outside paragraphs is not clear.
            if token.type in (Token.TYPE_SPACE, Token.TYPE_NEWLINE):
                whitespace = Whitespace(token.start, token.end, (), token.value)
                whitespace._root = self.results
                whitespace._depth = 1
                self.results.append(whitespace)
                self.advance_token()
                if token.type == Token.TYPE_NEWLINE:
                    self.line_num += 1
                continue
            elif token.type == Token.TYPE_TEXT:
                text = Text(token.start, token.end, (), token.value)
                text._root = self.results
                text._depth = 1
                self.results.append(text)
                self.advance_token()
                continue

            # TODO insert (start,end) pairs before each element so it's easier/faster to search?
            # TODO interaction of milestones with yield

            # Handle markers, attributes. 

            if token.type != Token.TYPE_ATTRIBUTE:
                marker = self.marker_from_token(token)
            if self.DEBUG:
                print('\tmarker = {}'.format(marker))
            if token.type == Token.TYPE_MARKER_START and marker not in ('c', 'v'):
                # Parse USFM as a series of paragraph markers.

                # Avoid handling \c specially. Provide a better mechanism for handling
                # \c and \v "contents" that respects USFM structure (e.g. handles overlapping)
                # Because of this, Paragraph elements have children - Text and Character/Note
                # elements intermingled, and certain Character / Note elements have children
                # (e.g. \f \ft some text \f*), but Paragraphs don't have a parent, to support
                # e.g. quotations going across chapter bounds

                if marker in PARAGRAPH_MARKER_ELEMENTS:
                    if self.DEBUG:
                        print('\t parsing paragraph, token={}, marker={}'.format(token, marker))
                    paragraph = self.parse_paragraph_marker()
                    # paragraphs are top-level elements. If generating, don't reference .results
                    self.results.append(paragraph)
                # Handle \v, and \fr, \ft and similar character markers without an end 
                # all together in parse_span_marker()

                elif marker[0].lower() == 'z':
                    if self.DEBUG:
                        print('\t custom = {}'.format(token))
                    pass

                else:
                    if marker in ALL_EXISTING_MARKERS or marker.endswith('-s') or marker.endswith('-e'):
                        e = USFMSyntaxError("[~ {}] \\{} marker cannot occur in this context".format(
                            self.line_num, marker
                        ))
                        self.results.append(ParsingFailedElement(token.start, e))
                        raise e
                    else:
                        e = NonExistentMarkerError("[~ {}] \\{} is not a marker in USFM".format(
                            self.line_num, marker
                        ))
                        self.results.append(ParsingFailedElement(token.start, e))
                        raise e


            # C occurs only at top level (no parents, handled by main loop)
            # V occurs only within paragraph
            elif token.type == Token.TYPE_MARKER_START and marker == 'c':
                if self.DEBUG:
                    print('\tdoing milestone_c_v()')
                c_milestone = self.milestone_c_v()
                c_milestone._depth = 1
                self.results.chapters[ c_milestone.value ] = c_milestone
                self.results.append(c_milestone)
                self.advance_token()

            elif token.type == Token.TYPE_MARKER_START and marker == 'v':
                e = USFMSyntaxError("[~ {}] \\v cannot occur in this context".format(
                    self.line_num
                ))
                self.results.append(ParsingFailedElement(token.start, e))
                raise e

            elif token.type == Token.TYPE_MARKER_END:
                self.advance_token()
                if not self.current_token():
                    if self.DEBUG:
                        print('MAIN LOOP DONE token = {}'.format(token))
                else:
                    # handle milestones
                    self.retreat_token()
                    if token.value.endswith('\\*'):
                        milestone = self.milestone()
                    elif self.marker_from_token(token.value) in ('c', 'v'):
                        milestone = self.milestone_c_v()
                        if isinstance(milestone, C):
                            self.results.chapters[milestone.value] = milestone
                    else:
                        raise ParserError("[~ {}] Unhandled".format(self.line_num))
                    milestone._depth = 1
                    self.results.append(milestone)
                    self.advance_token()

            else:
                raise ParserError("[~ {}] Unhandled, token = {}".format(self.line_num, token))

        if self.try_bound > self.parsing_bound:
            self.parsing_bound = self.try_bound

    def marker_from_token(self, token, matching=False):
        """Return marker (not Element) for provided token (e.g. '\\p ' -> 'p', '\\w*' -> 'w'),
            marker includes '+' if appropriate - different from marker_from_token()      
            '\\+w' -> 'w'. Returns milestone marker tokens '\\qt-s\\*' -> 'qt-s'.
            If a number marker, return without numbering. Enforces lowercase. If not

            a marker, or None, returns an empty string. If matching True, keep +"""
        if token == None:
            return ''
        if not isinstance(token, Token):
            raise ParserError("marker_from_token() got non-Token, not None")
        if not token.value.startswith('\\'):
            return ''
        tmp = token.value.replace('\\', '')
        tmp = tmp.replace('*', '')
        if not matching:
            tmp = tmp.replace('+', '')
        tmp = re.sub(r'\s+|\d+', '', tmp)
        # don't strip -
        tmp = tmp.lower()
        return tmp

    def _marker_number_from_token(self, token):
        m = re.search(r'\d+', token.value)
        if m:
            return int(m.group(0))
        else:
            return None

    def _first_number_in_string(self, s):
        """Return first number in string, AS TEXT"""
        m = re.match(r'[^\d]*(\d+)', s)
        if m:
            return m.group(1)
        else:
            return None

    def current_token(self):
        """Retrieve the current token without advancing through tokens. This returns
           a Token or None."""
        if self.try_bound < len(self.tokenizer.tokens):
            return self.tokenizer.tokens[self.try_bound]
        else:
            return None

    def next_token(self):
        """Retrieve next token. Calling this means we expect there to be a next token,
           so raise exception if there isn't one."""
        self.try_bound += 1
        if self.try_bound < len(self.tokenizer.tokens):
            return self.tokenizer.tokens[self.try_bound]
        else:
            raise NoTokenError("No next token but next token requested")

    def advance_token(self):
        self.try_bound += 1

    def retreat_token(self):
        self.try_bound -= 1

    def last_token(self):
        if self.tokenizer.tokens:
            return self.tokenizer.tokens[-1]
        else:
            raise NoTokenError("Last token not retrievable")

    def get_results(self):
        return self.results

    def yield_results(self):
        # TODO
        while self.results:
            element = self.results.popleft()
            yield element

    # These methods parse using tokens, the element classes themselves can (sometimes) parse from strings
    # Element class parse methods are not used here.


    # - performance - tokenize so this isn't used?

    def collapse_text(self, include_types):
        """Retrieve all text in consecutive tokens with types in include_types. Returns
        appropriate text type."""

        token = self.current_token()
        if not token:
            return None

        text = ''
        start = token.start
        end = token.end

        seen_types = set()

        if type(include_types) == int:
            include_types = [include_types]

        self.try_bound_before = self.try_bound
        while token and token.type in include_types:
            seen_types.update([token.type])
            text += token.value
            end = token.end
            self.advance_token()
            token = self.current_token()
        self.try_bound_after = self.try_bound

        # if loop had iteration, adjust self.try_bound so succeeding .next_token() doesn't skip a token
        if self.try_bound_after != self.try_bound_before:
            self.retreat_token()

        if text:
            if Token.TYPE_TEXT in seen_types:
                return Text(start, end, (), text)
            else:
                return Whitespace(start, end, (), text)
        else:
            return None

    def milestone(self):
        """Return a Milestone, **except** C and V."""
        token = self.current_token()
        if '-' in token.value:
            # start/end milestone
            parts = self.get_marker_from_token(token).split('-')
            marker = parts[0].lower()
            if marker not in CHARACTER_MARKER_ELEMENTS and marker not in NOTE_MARKER_ELEMENTS:
                raise InvalidMarkerError("Not a valid start/end milestone marker ({}) - not a form of character/note marker".format(token.value))
            if marker in CHARACTER_MARKER_ELEMENTS:
                marker_class = CHARACTER_MARKER_ELEMENTS[marker]
            elif marker in NOTE_MARKER_ELEMENTS:
                marker_class = NOTE_MARKER_ELEMENTS[marker]

            # These parts are parsable separately - and hence no in SPAN_MARKER_PAIRS
            if parts[1].lower() == 's':
                # start
                elem = PairedMilestoneMarkerElement(
                    start=token.start, end=token.end, 
                    marker=marker, marker_raw=token.value, 
                    milestone_type=PairedMilestoneMarkerElement.TYPE_START
                )
                if self.DEBUG:
                    print('(converted) {}'.format(elem))
                elem._root = self.results
                self._last_paired_milestone_markers[marker] = elem
                return elem
                
            elif parts[1].lower() == 'e':
                # end
                if marker not in self._last_paired_milestone_markers[marker]:
                    raise ParserError("[~ {}] Failed to pair paired marker ({})".format(
                        self.line_num, marker
                    ))
                elem = PairedMilestoneMarkerElement(
                    start=token.start, end=token.end, 
                    marker=marker, marker_raw=token.value,
                    milestone_type=PairedMilestoneMarkerElement.TYPE_END
                )
                if self.DEBUG:
                    print('(converted) {}'.format(elem))
                elem._root = self.results
                return elem
            else:
                raise InvalidMarkerError("Marker is not valid ({}). Not start/end, and standalone marker should not contain -".format(token.value))
        else:
            # standalone milestone
            marker = self.marker_from_token(token)
            if marker not in MILESTONE_MARKER_ELEMENTS:
                raise InvalidMarkerError("marker {} is not a milestone marker",format(marker))
            marker_class = MILESTONE_MARKER_ELEMENTS[marker]
            elem = marker_class(token.start, token.end, marker, token.value)
            elem._root = self.results
            if self.DEBUG:
                print('\t(converted) {}'.format(elem))
            return elem

    def milestone_c_v(self):
        """Insert \\c or \\v milestones (not handled above since they don't use syntax
           of milestones). they parse as milestones."""
        token = self.current_token()
        marker = self.marker_from_token(token)
        marker_raw = token.value
        self.advance_token()
        while self.current_token().type in (Token.TYPE_SPACE, Token.TYPE_NEWLINE):
            marker_raw += self.current_token().value
            self.advance_token()
        
        marker_class = self.get_marker_class(marker)
        if self.DEBUG:
            print('\tmilestone_c_v: token = {}, marker = {}, marker_class = {}, advanced to {}'.format(
                token, marker, marker_class, self.current_token()
            ))
        
        value = marker_class.convert(self.current_token().value)
        marker_class.validate(value)
        elem = marker_class(
                start=token.start, 
                end=self.current_token().end, 
                marker=marker, 
                marker_raw=marker_raw, 
                value=value
        )
        elem._root = self.results
        if isinstance(elem, C):
            self._current_chapter_marker = elem
            self._current_verse_marker = None

        # set current chapter if C, attach chapter marker if V
        elif isinstance(elem, V):
            self._current_verse_marker = elem

            # 
            if self._current_chapter_marker != None:
                elem.parents.append(self._current_chapter_marker)
                self._current_chapter_marker.children.append(elem)
        if self.DEBUG:
            print("\t(converted) {}".format(elem))
        return elem

    def parse_paragraph_marker(self):
        # Non-recursive - paragraph elements are not contained in other paragraph elements.
        start_token = self.current_token()
        if self.DEBUG:
            print('PARA, start token = {}'.format(start_token))

        self.line_num += start_token.value.count('\n')  # TODO

        start_ctm = self.marker_from_token(start_token)
        if self.DEBUG:
            print('\tstart ctm = {}'.format(start_ctm))

        start_marker_class = self.get_marker_class(start_ctm)
        if self.DEBUG:
            print('\tstart marker class = {}'.format(start_marker_class.__name__))

        # start_marker_class cannot be a milestone.
        assert(not issubclass(start_marker_class, MilestoneMarkerElement))

        # Handle any other Paragraph. chapter parent set in main loop.
        # These don't have parents
        start_elem = start_marker_class(start_token.start, 0, start_ctm, start_token.value, ())
        start_elem._depth = 1

        # Handle numbering
        if issubclass(start_marker_class, NumberedElement):
            number = self._first_number_in_string(start_token.value)
            if number == None:
                if start_ctm in ('toc', 'toca'):
                    e = InvalidMarkerError("\\{} must be numbered (e.g. \\{}1)".format(
                        start_ctm, start_ctm
                    ))
                    self.results.append(ParsingFailedElement(start_token.start, e))
                    raise e
                else:
                    start_elem.number = 1
            else:
                start_elem.number = int(number)

        # Handle elements until another paragraph element is found.
        self.advance_token()
        token = self.current_token()
        if not token:
            start_elem.end = start_token.end
            return start_elem
        else:
            self.line_num += token.value.count('\n')    # TODO
            marker = self.marker_from_token(token)

        if self.DEBUG: print('PARA LOOP starting, token = {}, marker = {}'.format(token, marker))

        while token and marker not in PARAGRAPH_MARKER_ELEMENTS and marker != 'c':
            # Collapse the longest run of text (without marker) we can
            plain_text = self.collapse_text((Token.TYPE_SPACE, Token.TYPE_NEWLINE, Token.TYPE_TEXT))
            if plain_text:
                self.line_num += plain_text.text.count('\n')    # TODO
                if self.DEBUG: print('\t(para) collapsed [{}]'.format(plain_text.get_text()))
                plain_text._depth = 2
                plain_text.parents.append(start_elem)
                start_elem.children.append(plain_text)
                if start_marker_class == D and self._current_verse_marker and self._current_verse_marker.value != 1:
                    start_elem._psalm_119_skip = True
                    self._prev_d_text = plain_text
            elif token.type == Token.TYPE_MARKER_START and marker == 'c':
                raise ParserError("[~ {}] Should not occur".format(self.line_num))
            elif token.type == Token.TYPE_MARKER_START and marker == 'v':
                v_milestone = self.milestone_c_v()
                v_milestone._depth = 2
                v_milestone.parents.append(start_elem)
                start_elem.children.append(v_milestone)
                
                if  self._prev_d_text:
                    
                    start_elem.children.append(self._prev_d_text)
                    self._prev_d_text = None
            elif token.type == Token.TYPE_MARKER_START \
            and (marker in CHARACTER_MARKER_ELEMENTS or marker in NOTE_MARKER_ELEMENTS):
                span = self.parse_span_marker()
                span.parents.append(start_elem)
                start_elem.children.append(span)
            elif token.type == Token.TYPE_MARKER_END and token.value.endswith('\\*'):
                milestone = self.milestone()
                milestone.parents.append(start_elem)
                start_elem.children.append(milestone)
                # TODO useful API for self-closing and start/end milestones that aren't c/v?
            else:
                if marker in ALL_EXISTING_MARKERS:
                    raise ParserError("[~line {}] Should not occur, token={}".format(
                        self.line_num, token
                    ))
                else:
                    raise NonExistentMarkerError("Marker \\{} does not exist in USFM".format(marker))

            self.advance_token()
            token = self.current_token()
            marker = self.marker_from_token(token)

        if self.DEBUG:
            print('PARA LOOP finishing, token = {}, marker = {}'.format(token, marker))

        # Determine exit cond
        if not token:
            # Finish whole parse, not just paragraph
            last_token = self.last_token()
            start_elem.end = last_token.end
            if self.DEBUG:
                print('PARSE finishing (para)')
        elif marker in PARAGRAPH_MARKER_ELEMENTS or marker == 'c':
            start_elem.end = token.start
        else:
            raise ParserError("[~ line {}] Should not occur - impossible".format(self.line_num))

        start_elem._root = self.results
        return start_elem
            
        # TODO adjust self.parsing_bound


    def parse_span_marker(self, depth=0):
        """A recursive method to parse span (character, note) markers.
           Returns a SpanMarkerElement subclass."""

        if hasattr(self, 'max_depth'):
            max_depth = int(self.max_depth)
        else:
            max_depth = int(self.DEFAULT_MAX_DEPTH)

        if depth > max_depth:
            e = ParserError("Maximum depth ({}) reached in parse_span_marker(), parsing failed. You might need to provide max_depth=N to the Parser constructor.".format(max_depth))
            self.results.append(ParsingFailedElement(self.current_token().start, e))
            raise e

        start_token = self.current_token()
        if self.DEBUG:
            print('SPAN, start token = {}'.format(start_token))

        self.line_num += start_token.value.count('\n')  # TODO

        # Sometimes, but not always, we ensure the span marker has
        # the appropriate closing marker (e.g. \add ... \add*, but not \v or \fr)
        start_ctm = self.marker_from_token(start_token);
        start_ctm_matching = self.marker_from_token(start_token, matching=True)
        if self.DEBUG:
            print('\tstart ctm = {}, start_ctm_matching = {}'.format(start_ctm, start_ctm_matching))

        start_marker_class = self.get_marker_class(start_ctm)

        # start_marker_class cannot be a milestone.
        assert(not issubclass(start_marker_class, MilestoneMarkerElement))

        start_elem = start_marker_class(start_token.start, 0, start_ctm, start_token.value, (), ())
        start_elem._depth = depth + 2

        # Handle all elements & attributes, recursively.
        token = self.next_token()        
        marker = self.marker_from_token(token)
        self.line_num += token.value.count('\n')    # TODO

        if self.DEBUG:
            print('SPAN LOOP starting, token = {}, marker = {}'.format(token, marker))

        while token and marker not in PARAGRAPH_MARKER_ELEMENTS and marker != 'c':

            # Collapse the longest run of text (without marker) we can
            plain_text = self.collapse_text((Token.TYPE_SPACE, Token.TYPE_NEWLINE, Token.TYPE_TEXT))
            if plain_text:
                self.line_num += plain_text.text.count('\n')    # TODO
                if self.DEBUG:
                    print('\t(span) collapsed [{}]'.format(plain_text.get_text()))
                plain_text._depth = start_elem._depth + 1
                plain_text.parents.append(start_elem)
                start_elem.children.append(plain_text)
                if self.DEBUG:
                    print('\t after collapse token = {}'.format(self.current_token()))
                
            elif marker == 'v':
                v_milestone = self.milestone_c_v()
                v_milestone._depth = start_elem._depth + 1
                v_milestone.parents.append(start_elem)
                start_elem.children.append(v_milestone)
            elif marker in CHARACTER_NOTE_MARKERS_NO_END:
                # Handle this here because a) doesn't recurse b) simpler to keep parents
                self.advance_token()
                text = self.collapse_text((Token.TYPE_SPACE, Token.TYPE_NEWLINE, Token.TYPE_TEXT))
                if not text:
                    e = USFMSyntaxError("[{} ~line {}] {} requires following text".format(
                        getattr(self, '_file', ''), self.line_num, marker
                    ))
                    self.results.append(ParsingFailedElement(token.start, e))
                    raise e
                self.line_num += text.text.count('\n')  # TODO
                text._depth = start_elem._depth + 2
                marker_class = self.get_marker_class(marker)
                elem = marker_class(token.start, text.end, marker, token.value + text.text, (start_elem), (text,))
                text.parents.append(elem)
                elem._depth = start_elem._depth + 1
                if self.DEBUG:
                    print('\t(converted no end) {}'.format(elem))
                start_elem.children.append(elem)
            elif marker in SPAN_MARKERS_PAIR and token.type == Token.TYPE_MARKER_START:
                if self.DEBUG:
                    print('\t recursion, token = {}'.format(self.current_token()))
                span_marker = self.parse_span_marker(depth+1)
                span_marker.parents.append(start_elem)
                start_elem.children.append(span_marker)
            elif token.type == Token.TYPE_ATTRIBUTE:
                # Attributes belong to this Character / Note marker
                if start_elem.attributes:
                    e = InvalidMarkerError("Marker {} contains more than 1 set of attributes".format(ctm))
                    self.results.append(ParsingFailedElement(token.start, e))
                    raise e
                start_elem.attributes = start_elem.parse_attributes(token.value)
                start_elem.attributes_raw = token.value
                if self.DEBUG:
                    print('\tgot attributes = {}'.format(start_elem.attributes))
            elif token.type == Token.TYPE_MARKER_END:
                if token.value.endswith('\\*'):
                    start_elem.children.append(self.milestone())
                else:
                    # Close - verify
                    if token.value != '\\' + start_ctm_matching + '*':
                        e = ParserError("[~ {}] Close token {} doesn't match opening token {}".format(
                            self.line_num, token, start_token
                        ))
                        self.results.append(ParsingFailedElement(token.start, e))
                        raise e
                    if self.DEBUG:
                        print('\tverified marker end ctm = {}, token = {}'.format(
                            start_ctm, token
                        ))
                    start_elem.end = token.end
                    # Include end marker raw in start elem
                    start_elem.end_marker_raw = token.value
                    # no span loop, drop back to para loop
                    if self.DEBUG:
                        print('SPAN LOOP finishing, found matching \\{}'.format(start_ctm))
                    
                    # If we have a matching close marker, we've completed span parse
                    # don't advance token - we return to parse_paragraph and that does it
                    start_elem._root = self.results
                    return start_elem
            else:
                raise ParserError("[~ {}] Should not occur, token = {}, marker = {}".format(
                    self.line_num, token, marker
                ))

            self.advance_token()
            token = self.current_token()
            marker = self.marker_from_token(token)

        # Determine exit cond
        if not token:
            last_token = self.last_token()
            start_elem.end = last_token.end
            if self.DEBUG:
                print('SPAN LOOP finishing, no more tokens')
        elif marker in PARAGRAPH_MARKER_ELEMENTS or marker == 'c':
            if self.DEBUG:
                print('SPAN LOOP finishing, got paragraph marker or c, token = {}'.format(token))
            
        start_elem._root = self.results
        return start_elem
    


# TODO self-closing and non c/v milestone API doesn't exist
# TODO iterate chapters in book, iterate verses in chapter - does that work w multi dimensions
# TODO error marker = marker1 — The unnumbered version may be used when only one level of marker exists within the project text. Numbers should always be included when more than one level of the marker exists within the project text.
# TODO warning The variable # should not be used to indicate a specific occurrence in scripture of the element type (e.g. using \s3 to represent the location of the particular section heading before the “Story of Creation” in Genesis 1.)
# TODO legacy modes (< 2.4, ...?)
# TODO warning not text follow \b
# TODO warn deprecated
# TODO given a text, return markers used
# TODO is there more then 2 dimensions of metaphor in USFM? if not, use single elem parent?







# TODO CLI tools.
# - fragments (1 line \\v sdkjflksjfdlk

# - correctly, paragraph-at-a-time
