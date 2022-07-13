# -*- coding: UTF-8 -*-

import re
import collections

from .Token import Token

from ..Constants import SPACES, NEWLINES

class TokenizerResults(collections.deque):

    def __repr__(self):
        out = '{}([\n'.format(self.__class__.__name__)
        for elem in self:
            out += '\t{}\n'.format(elem)
        out += '])\n'
        return out

class Tokenizer:
    """A plain text tokenizer""" 

    def __init__(self, text='', strict=False, discard_after_tokenizing=True):
        self.text = text            # text to be tokenized
        self.tokens = TokenizerResults()
        self.tokenizing_bound = 0   # offset in 'text' up to which tokenizing is complete. 
        self.discard_after_tokenizing = discard_after_tokenizing

        self.DEBUG = 0
        self._punct = '.:;‘“”?!()‐‑‒–—―~`@#$%^&*+=|\\\'"<>/'       # no hyphen, no ’

        self._punct_dict = {y: 1 for y in self._punct}

        self.tokenizing_regex = r'''
            # Word
            [-’\w]+
            |
            # Punct
            [''' + self._punct + r''']
            |
            # Comma
            [,]
            |
            # Newlines
            (?: \r\n | \r | \n )
            |
            # Space
            [ \t]
        '''     

    def add(self, text):
        self.text += text

    def reset(self):
        """Reset entire state of tokenizer"""
        self.text = ''
        self.tokens = TokenizerResults()
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

            if match.group(0)[0] in self._punct_dict:
                self.tokens.append(self._create_token_from_match(Token.TYPE_PUNCT, match))
            elif match.group(0) in NEWLINES:
                self.tokens.append(self._create_token_from_match(Token.TYPE_NEWLINE, match))
            elif match.group(0) in SPACES:
                self.tokens.append(self._create_token_from_match(Token.TYPE_SPACE, match))
            elif match.group(0) == ',':
                self.tokens.append(self._create_token_from_match(Token.TYPE_COMMA, match))
            else:
                
                self.tokens.append(self._create_token_from_match(Token.TYPE_WORD, match))

            try_bound = match.end()

            # TODO - newline grouping?

        if try_bound != 0:
            self.tokenizing_bound += try_bound
