# -*- coding: UTF-8 -*-

import re
import collections

import pprint

from .Token import Token
from .Constants import SPACES, NEWLINES


class TokensDeque(collections.deque):

    def __repr__(self):
        out = 'TokensDeque([\n'
        for elem in self:
            out += '\t{}\n'.format(elem)
        out += '])\n'
        return out

class Tokenizer:
    """A USFM tokenizer designed to handle partial data (not requiring whole USFM file)"""

    def __init__(self, text='', strict=False, discard_after_tokenizing=True):
        self.text = text            # text to be tokenized
        self.tokens = TokensDeque()
        self.tokenizing_bound = 0   # offset in 'text' up to which tokenizing is complete. 
        self.discard_after_tokenizing = discard_after_tokenizing

        self.DEBUG = 0

        self.tokenizing_regex = '''
            # Paragraph marker, or Begin Character or Note marker
            \\\\[+\w]+[\n\r \t]
            |
            # End - Character or Note marker or Milestone
            \\\\[-+\w]+(?:\\\\)?\*
            |
            # Attributes
            (?: \| (?: \w+ (?:=)? ( (?:"[^"]+?") | (?:\w+) )? \s* )+ )
            |
            # Text
            (?!<\\\\)[^|\\\\ \t\r\n]+         # Negative lookbehind required if tokenizing gradually
            |
            # Newlines
            [\n\r]+
            |
            # Space
            [ \t]
        '''     
    
    # TODO whitespace - preservation and chunking with +

    def add(self, text):
        self.text += text

    def reset(self):
        """Reset entire state of tokenizer"""
        self.text = ''
        self.tokens = TokensDeque()
        self.tokenizing_bound = 0

    def _create_token_from_match(self, token_type, match):
        return Token(
            token_type,
            match.group(0),
            self.tokenizing_bound + match.start(),
            self.tokenizing_bound + match.end()
        )

    def tokenize(self):
        """Tokenize as far as possible in 'text'.
            If discard_after_tokenizing is set, discard the tokenized text."""
        try_bound = 0

        for match in re.finditer(self.tokenizing_regex, self.text[self.tokenizing_bound:], re.X):
            if self.DEBUG:
                print("TOKENIZER match = {}".format(match))
            # Ensure all text > self.tokenizing_bound tokenized.
            # Matches in subsequent tokenize() calls have match.start() == 0, 
            if match.start() != try_bound:
                break

            # When creating tokens, add try_bound to self.tokenizing_bound
            # to get correct offsets

            if match.group(0)[0] == '\\':
                if match.group(0)[-1] == '*':
                    self.tokens.append(
                        self._create_token_from_match(Token.TYPE_MARKER_END, match)
                    )
                else:
                    self.tokens.append(
                        self._create_token_from_match(Token.TYPE_MARKER_START, match)
                    )
            elif match.group(0)[0] == '|':
                self.tokens.append(self._create_token_from_match(Token.TYPE_ATTRIBUTE, match))
            elif match.group(0) in NEWLINES:
                self.tokens.append(self._create_token_from_match(Token.TYPE_NEWLINE, match))
            elif match.group(0) in SPACES:
                self.tokens.append(self._create_token_from_match(Token.TYPE_SPACE, match))
            else:
                self.tokens.append(self._create_token_from_match(Token.TYPE_TEXT, match))

            try_bound = match.end()

            # TODO - newline grouping?

        if try_bound != 0:
            self.tokenizing_bound += try_bound


