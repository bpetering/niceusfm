# -*- coding: UTF-8 -*-                                                                                            

import sys 
from os.path import dirname
sys.path.append(dirname(dirname(sys.path[0])))

from usfmparser.Exceptions import (
        ParserError, InvalidMarkerError, NonExistentMarkerError,
        USFMSyntaxError
)

from usfmparser.Parser import Parser, ParserResults
from usfmparser.Token import Token

from usfmparser.Elements.Text import Text
from usfmparser.Elements.Whitespace import Whitespace
from usfmparser.Elements.MarkerElement import MarkerElement
from usfmparser.Elements.TextElement import TextElement
from usfmparser.Elements.ParentElement import ParentElement

from usfmparser.Elements.ParagraphMarkerElements import (
    ID, IDE, H, TOC, MT, MS,
    S, SP, P, M, PI, MI, NB, PC, B, P,
    Q, LI,
    ParagraphMarkerElement,
    PARAGRAPH_MARKER_ELEMENTS
)
from usfmparser.Elements.CharacterMarkerElements import (
    W, BK, WJ,
    CharacterMarkerElement,
    CHARACTER_MARKER_ELEMENTS
)
from usfmparser.Elements.NoteMarkerElements import (
    F, FE, X, FR, FT,
    NoteMarkerElement,
    NOTE_MARKER_ELEMENTS
)
from usfmparser.Elements.MilestoneMarkerElements import (
    C, V,
    MilestoneMarkerElement,
    PairedMilestoneMarkerElement,
    MILESTONE_MARKER_ELEMENTS
)















# branch coverage?
# parameterized tests (fake data)?



# helpers
def first_marker_index(results):
    i = 0
    while i < len(results):
        if isinstance(results[i], MarkerElement):
            return i
        i += 1
    raise ValueError("No marker elements in results")

def first_instance_index(results, cls):
    i = 0
    while i < len(results):
        if isinstance(results[i], cls):
            return i
        i += 1
    raise ValueError("No {} instance in results".format(cls.__name__))
#####
##### WHITESPACE
#####
n = Parser('\\p ')
n.parse()
assert(n.results)
assert(len(n.results) == 1)
assert(isinstance(n.results[0], P))
assert(n.results[0].get_text() == ' ')
assert(n.results[0].marker == 'p')
assert(n.results[0].marker_raw == '\\p ')
assert(n.results[0].get_marker_raw() == '\\p ')



assert(n.results[0].get_marker_raw() == '\\p ')

n = Parser('\\p\n')
n.parse()
assert(n.results)
assert(len(n.results) == 1)
assert(isinstance(n.results[0], P))
assert(n.results[0].get_text() == '\n')


n = Parser('\\p\t')
n.parse()
assert(n.results)
assert(len(n.results) == 1)
assert(isinstance(n.results[0], P))
assert(n.results[0].get_text() == '\t')

# TODO normalization - within \\p
# TODO normalizaiton - preceding para marker



#####
##### PARAGRAPH
#####



n = Parser('\\p ')
n.parse()
assert(n.results)
assert(len(n.results) == 1)
assert(isinstance(n.results[0], P))
assert(n.results[0].start == 0)
assert(n.results[0].end == 3)
assert(n.results[0].marker == 'p')
assert(n.results[0].marker_raw == '\\p ')
assert(n.results[0].get_marker() == 'p')
assert(n.results[0].get_marker_raw() == '\\p ')

assert(n.results[0].get_text() == ' ')
#assert(n.results[0].get_parsed() == '')

z = Parser('\\p Something')
z.parse()
assert(z.results)
assert(len(z.results) == 1)
assert(isinstance(z.results[0], P))
assert(z.results[0].start == 0)
assert(z.results[0].end == 12)
assert(z.results[0].children)
assert(len(z.results[0].children) == 1)
assert(isinstance(z.results[0].children[0], Text))
assert(z.results[0].children[0].get_text() == 'Something')
assert(z.results[0].children[0].get_parsed() == 'Something')

z = Parser('\\h Genesis')
z.parse()
assert(z.results)
assert(len(z.results) == 1)
assert(isinstance(z.results[0], H))
assert(z.results[0].start == 0)
assert(z.results[0].end == 10)
assert(z.results[0].get_text() == ' Genesis')
assert(z.results[0].marker == 'h')
assert(z.results[0].get_marker() == 'h')
assert(z.results[0].marker_raw == '\\h ')



assert(z.results[0].get_marker_raw() == '\\h ')
assert(len(z.results[0].children) == 1)
assert(z.results[0].children[0].get_text() == 'Genesis')
assert(z.results[0].children[0].text == 'Genesis')
assert(z.results[0].children[0].start == 3)
assert(z.results[0].children[0].end == 10)






z = Parser('\\c 1')
z.parse()
assert(z.results)
assert(len(z.results) == 1)
assert(isinstance(z.results[0], C))
assert(z.results[0].marker == 'c')
assert(z.results[0].value == 1)
assert(z.results[0].start == 0)
assert(z.results[0].end == 4)
assert(z.results[0].get_value() == 1)
assert(z.results[0].get_text() == ' 1')


z = Parser('\\v 1')
try:
    z.parse()
except USFMSyntaxError:
    pass
else:
    assert(False)

#assert(not z.results)


z = Parser('\\toc1 Something')
z.parse()
assert(z.results)
assert(len(z.results) == 1)
assert(isinstance(z.results[0], TOC))
assert(z.results[0].number == 1)
assert(z.results[0].marker_raw == '\\toc1 ')
assert(z.results[0].get_text() == ' Something')
assert(z.results[0].children)
assert(z.results[0].children[0].get_text() == 'Something')

z = Parser('\\toc1 Song of Solomon\n\\toc2 Song of Someone Else')
z.parse()
assert(z.results)
assert(len(z.results) == 2)
assert(isinstance(z.results[0], TOC))
assert(z.results[0].number == 1)
assert(z.results[0].marker == 'toc')
assert(z.results[0].get_text() == ' Song of Solomon\n')      # need newline
#assert(z.results[0].get_parsed() == 'Song of Solomon\n')
assert(isinstance(z.results[1], TOC))
assert(z.results[1].number == 2)
assert(z.results[1].marker == 'toc')
assert(z.results[1].get_text() == ' Song of Someone Else')
#assert(z.results[1].get_parsed() == 'Song of Someone Else')



z = Parser('\\p \\c 1\\v 2')     
try:
    z.parse()
except USFMSyntaxError:
    pass
else:
    assert(False)
#assert(not z.results)

n = Parser('\\c 1\\p\n\\v 2')
n.parse()
assert(n.results)
assert(len(n.results) == 2)
assert(isinstance(n.results[0], C))
assert(not hasattr(n.results[0], 'children'))
assert(n.results[0].value == 1)
assert(n.results[0].get_value() == 1)
assert(n.results[0].get_text() == ' 1')

assert(isinstance(n.results[1], P))
assert(n.results[1].get_text() == '\n 2')
assert(n.results[1].children)
# get_parsed() should always include whitespace within an element and part of a marker
assert(len(n.results[1].children) == 1)
assert(isinstance(n.results[1].children[0], V))
assert(n.results[1].children[0].value == 2)
assert(n.results[1].children[0].get_value() == 2)
assert(n.results[1].children[0].get_text() == ' 2')

# TODO normalization
#z = Parser('\\c 1\n \\q\n\\v 2')     
#z.parse()
#assert(z.results)
#assert(len(z.results) == 2)
#assert(isinstance(z.results[0], C))
#assert(z.results[0].value == 1)
#assert(z.results[0].get_value() == 1)
#assert(z.results[0].marker_raw == '\\c 1')

# TODO normalization assert(z.results[0].get_text() == '1\n 

#assert(isinstance(z.results[1], Q))
#assert(z.results[1].number == 1)
#assert(z.results[1].marker_raw == '\\q\n')
#assert(z.results[1].children)
#assert(len(z.results[1].children) == 1)
#assert(z.results[1].children[0] == V(9, 13, 'v', 2))


p = Parser('\\p \\w something|strong="H1234"\\w* \\w else|strong="G1234"\\w*')
p.parse()
assert(p.results)
assert(len(p.results) == 1)
assert(p.results[0].children)
assert(len(p.results[0].children) == 3)
assert(isinstance(p.results[0].children[0], W))
assert(isinstance(p.results[0].children[1], Whitespace))
assert(isinstance(p.results[0].children[2], W))
assert(p.results[0].children[0].get_text() == ' something')
assert(p.results[0].children[0].get_value() == 'something')
assert(p.results[0].children[0].attributes)
assert(p.results[0].children[0].attributes['strong'] == 'H1234')
assert(p.results[0].children[2].get_text() == ' else')
assert(p.results[0].children[2].get_value() == 'else')
assert(p.results[0].children[2].attributes)
assert(p.results[0].children[2].attributes['strong'] == 'G1234')


# \toc needs a number (no default to 1)
z = Parser('\\toc Foo')
try:
    z.parse()
except InvalidMarkerError:
    pass
else:
    assert(False)
#assert(not z.results)


# mt defaults to 1
z = Parser('\\mt Foo')
z.parse()
assert(z.results)
assert(isinstance(z.results[0], MT))
assert(z.results[0].number == 1)

# non-existent element completes, correct exception
z = Parser('\\quux ')
try:
    z.parse()
except NonExistentMarkerError:
    pass
else:
    assert(False)
#assert(not z.results)



n = Parser('\\c 1\n\\p\n\\v  1 Something else \\w something|strong="G5678"\\w*')
n.parse()
assert(n.results)
assert(len(n.results) == 3)
assert(n.results[0] == C(start=0, end=4, marker='c', value=1))
assert(not n.results[0].parents)
assert(n.results[1] == Whitespace(start=4, end=5, text='\n'))
assert(isinstance(n.results[2], P))
assert(n.results[2].children)
assert(len(n.results[2].children) == 3)
assert(isinstance(n.results[2].children[0], V))
assert(isinstance(n.results[2].children[1], Text))
assert(n.results[2].children[1].get_text() == ' Something else ')
assert(isinstance(n.results[2].children[2], W))
assert(n.results[2].children[2].get_text() == ' something')
assert(n.results[2].children[2].attributes)
assert(n.results[2].children[2].attributes['strong'] == 'G5678')


# Be careful about whitespace in these
z = Parser('''
        \\id SNG World English Bible (WEB)
    \\ide UTF-8
    \\h Song of Solomon
    \\toc1 The Song of Solomon
    \\toc2 Song of Solomon
    \\toc3 Song of Solomon
    \\mt1 The Song of Solomon
    \\c 1
    \\p

''')
z.parse()


assert(z.results)
assert([x.default_marker for x in z.results if isinstance(x, MarkerElement)] == ['id', 'ide', 'h', 'toc', 'toc', 'toc', 'mt', 'c', 'p'])
tmp = list(z.results)
tmp.reverse()
assert(isinstance(tmp[first_marker_index(tmp)], P))

# get text raw includes marker and closing marker - everything for those offsets

first_i = first_marker_index(z.results)
assert(isinstance(z.results[first_i], ID))
assert(z.results[first_i].get_text() == ' SNG World English Bible (WEB) \n    ')
assert(z.results[first_i].get_parsed() == ' SNG World English Bible (WEB)\n    ')
assert(z.results[first_i].get_value() == 'SNG World English Bible (WEB)')

assert(isinstance(z.results[first_i+1], IDE))
assert(z.results[first_i+1].get_text() == ' UTF-8\n    ')
assert(z.results[first_i+1].get_parsed() == ' UTF-8\n    ')
assert(z.results[first_i+1].get_value() == 'UTF-8')

assert(isinstance(z.results[first_i+2], H))
assert(z.results[first_i+2].get_text() == ' Song of Solomon \n    ')
assert(z.results[first_i+2].get_parsed() == ' Song of Solomon \n    ')
assert(z.results[first_i+2].get_value() == 'Song of Solomon')


assert(isinstance(z.results[first_i+3], TOC))
assert(z.results[first_i+3].number == 1)
assert(z.results[first_i+3].get_text() == ' The Song of Solomon \n    ')
assert(z.results[first_i+3].get_parsed() == ' The Song of Solomon \n    ')
assert(z.results[first_i+3].get_value() == 'The Song of Solomon')

assert(isinstance(z.results[first_i+4], TOC))
assert(z.results[first_i+4].number == 2)
assert(z.results[first_i+4].get_text() == ' Song of Solomon \n    ')
assert(z.results[first_i+4].get_parsed() == ' Song of Solomon \n    ')
assert(z.results[first_i+4].get_value() == 'Song of Solomon')

assert(isinstance(z.results[first_i+5], TOC))
assert(z.results[first_i+5].number == 3)
assert(z.results[first_i+5].get_text() == ' Song of Solomon    ')
assert(z.results[first_i+5].get_parsed() == ' Song of Solomon\n    ')
assert(z.results[first_i+5].get_value() == 'Song of Solomon')

assert(isinstance(z.results[first_i+6], MT))
assert(z.results[first_i+6].number == 1)
assert(z.results[first_i+6].get_text() == 'The Song of Solomon    ')
assert(z.results[first_i+6].get_parsed() == ' The Song of Solomon\n    ')
assert(z.results[first_i+6].get_value() == 'The Song of Solomon')

assert(isinstance(z.results[first_i+7], C))     # C must be top-level - not child of prev paragraph
assert(z.results[first_i+7].value == 1)

assert(isinstance(z.results[first_i+8], P))
assert(z.results[first_i+8].get_text() == '')
assert(z.results[first_i+8].get_parsed() == '\n\n')


n = Parser('''\\c 1
\\p
\\v 1  \\w In|strong="H5921"\\w* \\w the|strong="H5921"\\w* \\w third|strong="H7969"\\w* \\w year|strong="H8141"\\w*.
\\v 2  \\w The|strong="H0853"\\w* \\w Lord|strong="H0136"\\w*\\f + \\fr 1:2  \\ft The word translated “Lord” is “Adonai.”\\f* \\w gave|strong="H5414"\\w* \\w Jehoiakim|strong="H3079"\\w* \\w king|strong="H4428"\\w* \\w of|strong="H4428"\\w* \\w Judah|strong="H3063"\\w* \\w of|strong="H4428"\\w* \\w God|strong="H0430"\\w*;\\f + \\fr 1:2  \\ft The Hebrew word rendered “God” is “אֱלֹהִ֑ים” (Elohim).\\f* \\w and|strong="H0935"\\w* \\w he|strong="H0430"\\w* \\w carried|strong="H0935"\\w* \\w them|strong="H5414"\\w*
\\p
\\v 3  \\w The|strong="H0559"\\w* \\w king|strong="H4428"\\w* \\w spoke|strong="H0559"\\w* \\w to|strong="H0559"\\w* \\w Ashpenaz|strong="H0828"\\w*, \\w the|strong="H0559"\\w* \\w master|strong="H0559"\\w* \\w of|strong="H1121"\\w* \\w his|strong="H0935"\\w* \\w eunuchs|strong="H5631"\\w* \\w the|strong="H0559"\\w* \\w royal|strong="H4428"\\w* \\w offspring|strong="H2233"\\w*\\f + \\fr 1:3  \\ft or, seed\\f* \\w and|strong="H1121"\\w* \\w of|strong="H1121"\\w* \\w the|strong="H0559"\\w* \\w nobles|strong="H6579"\\w*:    
\\v 4  \\w youths|strong="H3206"\\w* \\w in|strong="H4428"\\w* \\w whom|strong="H0834"\\w* \\w was|strong="H0369"\\w*
''')
n.parse()
assert(n.results)
assert(len(n.results) == 3)
assert(isinstance(n.results[0], C))
assert(n.results[0].value == 1)

assert(isinstance(n.results[1], P))
assert(isinstance(n.results[2], P))



# same result w and wo \nb


#####
##### PARAGRAPH - REGRESSION
#####




#####
##### CHARACTER
#####

# Various places character markers cannot occur
n = Parser('\\f ')
try:
    n.parse()
except USFMSyntaxError:
    pass
else:
    assert(False)

n = Parser('\\w ')
try:
    n.parse()
except USFMSyntaxError:
    pass
else:
    assert(False)

n = Parser('\\fe ')
try:
    n.parse()
except USFMSyntaxError:
    pass
else:
    assert(False)

n = Parser('\\x ')
try:
    n.parse()
except USFMSyntaxError:
    pass
else:
    assert(False)


z = Parser('\\p \\w something\\w*')
z.parse()
assert(z.results)
assert(len(z.results) == 1)
assert(isinstance(z.results[0], P))
assert(z.results[0].children)
assert(len(z.results[0].children) == 1)
assert(z.results[0].children[0].start == 3)
assert(z.results[0].children[0].end == 18)
assert(z.results[0].children[0].get_text() == 'something')

z = Parser('\\p \\w something|strong="H1234"\\w*')
z.parse()
assert(z.results)
assert(len(z.results) == 1)
assert(isinstance(z.results[0], P))
assert(z.results[0].children)
assert(len(z.results[0].children) == 1)
assert(z.results[0].children[0].get_text() == 'something')


assert(z.results[0].children[0].start == 3)
assert(z.results[0].children[0].end == 33)
assert(z.results[0].children[0].attributes)
assert(z.results[0].children[0].attributes['strong'] == 'H1234')


n = Parser('\\q2 \\f \\fr 1:1 \\ft Some footnote text \\f*')
n.parse()
assert(n.results)
assert(len(n.results) == 1)
assert(isinstance(n.results[0], Q))
assert(n.results[0].number == 2)
assert(n.results[0].children)
assert(len(n.results[0].children) == 1)
assert(isinstance(n.results[0].children[0], F))
assert(n.results[0].children[0].children)
assert(len(n.results[0].children[0].children) == 2)
assert(isinstance(n.results[0].children[0].children[0], FR))
assert(n.results[0].children[0].children[0].value == '1:1')
assert(n.results[0].children[0].children[0].get_value() == '1:1')
assert(n.results[0].children[0].children[0].marker == 'fr')
assert(n.results[0].children[0].children[0].get_marker() == 'fr')
assert(n.results[0].children[0].children[0].marker_raw == '\\fr 1:1 ')
assert(n.results[0].children[0].children[0].get_marker_raw() == '\\fr 1:1 ')

assert(isinstance(n.results[0].children[0].children[1], FT))
assert(n.results[0].children[0].children[1].value == 'Some footnote text')
assert(n.results[0].children[0].children[1].get_text() == 'Some footnote text')
assert(n.results[0].children[0].children[1].get_value() == 'Some footnote text')
assert(n.results[0].children[0].children[1].marker == 'ft')
assert(n.results[0].children[0].children[1].get_marker() == 'ft')
assert(n.results[0].children[0].children[1].marker_raw == '\\ft Some footnote text ')
assert(n.results[0].children[0].children[1].get_marker_raw() == '\\ft Some footnote text ')



###### NESTING
# 'In USFM, character level markup is applied to text within a containing paragraph element like \p or \q1'
# 'All new character marker starts (without the + prefix) close all existing nesting.'
# 'Character markers occur in pairs, marking a span of text within a paragraph.'
# 'The Paratext translation editor will interpret the presence of a new marker as an implicit closure of any preceding character level marker.'
# '**Nested** character markers within notes always require explicit opening and closing markers, and must use the syntax for character marker nesting.'

z = Parser('\p Some text \\bk The Wars of Someone Else\\bk* were fought')
z.parse()
assert(z.results)
assert(len(z.results) == 1)
assert(isinstance(z.results[0], P))
assert(z.results[0].get_text() == 'Some text The Wars of Someone Else were fought')
assert(z.results[0].children)
assert(isinstance(z.results[0].children[0], BK))
assert(z.results[0].children[0].get_text() == 'The Wars of Someone Else')



n = Parser('\\id DAN 27-DAN-web.sfm World English Bible (WEB)')
n.parse()
assert(n.results)
assert(len(n.results) == 1)
assert(isinstance(n.results[0], ID))
assert(n.results[0].marker == 'id')
assert(n.results[0].get_text() == 'DAN 27-DAN-web.sfm World English Bible (WEB)')

n = Parser('\\h Daniel')
n.parse()
assert(n.results)
assert(len(n.results) == 1)
assert(isinstance(n.results[0], H))
assert(n.results[0].get_text() == 'Daniel')


z = Parser('\\f + \\fr 1:1 \\ft Some text \\f*')
z.parse()
assert(z.results)
assert(len(z.results) == 1)
assert(isinstance(z.results[0], F))
assert(z.results[0].children)
assert(len(z.results[0].children) == 3)
assert(isinstance(z.results[0].children[0], Text))      # TODO caller
assert(z.results[0].children[0].get_text() == '+')
assert(isinstance(z.results[0].children[1], FR))
assert(z.results[0].children[1].get_text() == '1:1')
assert(isinstance(z.results[0].children[2], FT))
assert(z.results[0].children[2].get_text() == 'Some text')


n = Parser('\\p \\wj \\+w something\\+w* else \\+w foo\\+w*\\wj*')
n.parse()
assert(n.results)
assert(len(n.results) == 1)
assert(isinstance(n.results[0], P))
assert(n.results[0].children)
assert(len(n.results[0].children) == 1)
assert(isinstance(n.results[0].children[0], WJ))
assert(n.results[0].children[0].children)
assert(len(n.results[0].children[0].children) == 3)
assert(isinstance(n.results[0].children[0].children[0], W))
assert(n.results[0].children[0].children[0].get_value() == 'something')
assert(isinstance(n.results[0].children[0].children[1], Text))
assert(n.results[0].children[0].children[1].get_value() == 'else')
assert(isinstance(n.results[0].children[0].children[2], W))
assert(n.results[0].children[0].children[2].get_value() == 'foo')



# Same, but with whitespace 
n = Parser('\\p \\wj \\+w something\\+w* else \\+w foo\\+w* \\wj*')
n.parse()
assert(n.results)
assert(len(n.results[0].children[0].children) == 4)
assert(isinstance(n.results[0].children[0].children[3], Whitespace))
assert(n.results[0].children[0].children[3].get_value() == ' ')






####### Whitespace
# '''Significant whitespace is a critical part of the USFM document and should always be preserved as is.
#
#       - The space after the end of a paragraph marker, or the end of the opening marker within a character or note marker pair.
#       - The newline preceding a new paragraph marker.'''


# '''Insignificant whitespace should be normalized by a USFM processor.
#
#       - Multiple whitespace within the body text of a paragraph.
#       - Multiple whitespace preceding a paragraph marker.'''


# 'All paragraph markers should be preceded by a single newline.'




####### Footnotes

z = Parser('\\w Sheol|strong="H1234"\\w*.\\f + \\fr 1:1  \\ft Sheol is the place of the dead. \\f*')
z.parse()
assert(z.results)
assert(len(z.results) == 3)     # period^
assert(isinstance(z.results[0], W))
assert(z.results[0].get_text() == 'Sheol')
assert(z.results[0].attribute['strong'] == 'H1234')
assert(isinstance(z.results[1], Text))
assert(z.results[1].get_text() == '.')
assert(isinstance(z.results[2], F))
assert(z.results[2].children)
assert(len(z.results[2].children) == 3)
assert(isinstance(z.results[2].children[0], Text))
assert(z.results[2].children[0].get_text() == '+')  # TODO caller?
assert(isinstance(z.results[2].children[1], FR))
assert(z.results[2].children[1].get_text() == '1:1')
assert(isinstance(z.results[2].children[2], FT))
assert(z.results[2].children[2].get_text() == 'Sheol is the place of the dead.')
assert(z.results[2].children[2].get_parsed() == 'Sheol is the place of the dead. ')


######
###### LOTS OF TEXT
######

z = Parser('''\\id SNG World English Bible (WEB)                               
\\ide UTF-8
\\h Song of Solomon 
\\toc1 The Song of Solomon 
\\toc2 Song of Solomon 
\\toc3 Song of Solomon 
\\mt1 The Song of Solomon 
\\c 1   
\\p
\\v 1  \\w The|strong="H0834"\\w* \\w Song|strong="H7892"\\w* \\w of|strong="H0834"\\w* \\w songs|strong="H7892"\\w*, \\w which|strong="H0834"\\w* \\w is|strong="H0834"\\w* \\w Solomon’s|strong="H8010"\\w*. 
\\sp Beloved 
\\q1
\\v 2 Let \\w him|strong="H3588"\\w* kiss \\w me|strong="H3588"\\w* \\w with|strong="H6310"\\w* \\w the|strong="H3588"\\w* \\w kisses|strong="H5390"\\w* \\w of|strong="H6310"\\w* \\w his|strong="H3588"\\w* \\w mouth|strong="H6310"\\w*; 
\\q2 \\w for|strong="H3588"\\w* \\w your|strong="H3588"\\w* \\w love|strong="H1730"\\w* \\w is|strong="H2896"\\w* \\w better|strong="H2896"\\w* \\w than|strong="H2896"\\w* \\w wine|strong="H3196"\\w*. 
\\q1
\\v 3  \\w Your|strong="H5921"\\w* \\w oils|strong="H8081"\\w* \\w have|strong="H0157"\\w* \\w a|strong="H5921"\\w* pleasing fragrance. 
\\q2 \\w Your|strong="H5921"\\w* \\w name|strong="H8034"\\w* \\w is|strong="H8034"\\w* \\w oil|strong="H8081"\\w* poured \\w out|strong="H5921"\\w*, 
\\q2 \\w therefore|strong="H3651"\\w* \\w the|strong="H5921"\\w* virgins \\w love|strong="H0157"\\w* \\w you|strong="H5921"\\w*.
''')
z.parse()

assert(z.results)
assert(len(z.results) > 20)
assert(z.results[first_instance_index(z.results, ID)].get_text() == 'SNG World English Bible (WEB)')
assert(z.results[first_instance_index(z.results, MT)].get_text() == 'The Song of Solomon')
assert(z.results[first_instance_index(z.results, V)].value == 1)

tmp = list(z.results)
tmp = tmp.reverse()
assert(z.results[first_instance_index(z.results, V)].value == 3)


z = Parser('''\\q2 \\w Jealousy|strong="H7068"\\w* \\w is|strong="H3820"\\w* \\w as|strong="H3588"\\w* \\w cruel|strong="H7186"\\w* \\w as|strong="H3588"\\w* \\w Sheol|strong="H7585"\\w*.\\f + \\fr 8:6  \\ft Sheol is the place of the dead. \\f*''')
z.parse()
assert(z.results)
assert(len(z.results) == 1)
assert(isinstance(z.results[0], Q))
assert(z.results[0].number == 2)
assert(z.results[0].get_text() == 'Jealousy is as cruel as Sheol.')
assert(z.results[0].get_text(include_footnotes=True) == 'Jealousy is as cruel as Sheol.+ 8:6  Sheol is the place of the dead.')



n = Parser('''\\p
\\v 1  \\w The|strong="H0834"\\w* \\w vision|strong="H2377"\\w* \\w of|strong="H1121"\\w* \\w Isaiah|strong="H3470"\\w* \\w the|strong="H0834"\\w* \\w son|strong="H1121"\\w* \\w of|strong="H1121"\\w* \\w Amoz|strong="H0531"\\w*, \\w which|strong="H0834"\\w* \\w he|strong="H0834"\\w* \\w saw|strong="H2372"\\w* \\w concerning|strong="H5921"\\w* \\w Judah|strong="H3063"\\w* \\w and|strong="H1121"\\w* \\w Jerusalem|strong="H3389"\\w*, \\w in|strong="H5921"\\w* \\w the|strong="H0834"\\w* \\w days|strong="H3117"\\w* \\w of|strong="H1121"\\w* \\w Uzziah|strong="H5818"\\w*, \\w Jotham|strong="H3147"\\w*, \\w Ahaz|strong="H0271"\\w*, \\w and|strong="H1121"\\w* \\w Hezekiah|strong="H2396"\\w*, \\w kings|strong="H4428"\\w* \\w of|strong="H1121"\\w* \\w Judah|strong="H3063"\\w*. 
\\q1
\\v 2  \\w Hear|strong="H8085"\\w*, \\w heavens|strong="H8064"\\w*, 
\\q2 \\w and|strong="H1121"\\w* \\w listen|strong="H8085"\\w*, \\w earth|strong="H0776"\\w*; \\w for|strong="H3588"\\w* \\w Yahweh|strong="H3068"\\w*\\f + \\fr 1:2  \\ft “Yahweh” is God’s proper Name, sometimes rendered “LORD” (all caps) in other translations.\\f* \\w has|strong="H3068"\\w* \\w spoken|strong="H1696"\\w*: 
\\q1 “\\w I|strong="H3588"\\w* \\w have|strong="H0776"\\w* nourished \\w and|strong="H1121"\\w* \\w brought|strong="H7311"\\w* \\w up|strong="H7311"\\w* \\w children|strong="H1121"\\w* 
\\q2 \\w and|strong="H1121"\\w* \\w they|strong="H1992"\\w* \\w have|strong="H0776"\\w* \\w rebelled|strong="H6586"\\w* \\w against|strong="H1696"\\w* \\w me|strong="H7311"\\w*.''')
n.parse()
assert(n.results)
assert(len(n.results) == 5)
assert(isinstance(n.results[0], P))
assert(isinstance(n.results[0], Q))
assert(isinstance(n.results[0], Q))
assert(isinstance(n.results[0], Q))
assert(isinstance(n.results[0], Q))










###### User-generated
n = Parser('\\zsomething foo')
n.parse()
assert(n.results)
assert(len(n.results) == 1)
assert(isinstance(n.results[0], ParagraphMarkerElement))
assert(n.results[0].marker == 'zsomething')
assert(n.results[0].get_text() == 'foo')



n = Parser('\\zSomethingElse foo bar bat \\f + \\fr 1:1 \\ft blah \\f*')
n.parse()
assert(n.results)
assert(len(n.results) == 1)
assert(isinstance(n.results[0], ParagraphMarkerElement))
assert(n.results[0].marker == 'zSomethingElse')
assert(n.results[0].children)
assert(len(n.results[0].children) == 7)     # TODO whitespace
assert(n.results[0].get_text() == 'foo bar bat + 1:1 blah')
assert(n.results[0].get_parsed() == 'foo bar bat + 1:1 blah ')





#######
####### Elements
#######

n = Parser('\\q2 \\w the|strong="H0935"\\w* \\w Holy|strong="H6918"\\w* \\w One|strong="H6918"\\w* \\w from|strong="H0935"\\w* \\w Mount|strong="H2022"\\w* \\w Paran|strong="H6290"\\w*. \\qs  \\+w Selah|strong="H5542"\\+w*.\\qs*')
n.parse()
assert(n.results)
assert(len(n.results) == 1)
assert(isinstance(n.results[0], Q))
assert(n.results[0].number == 2)
assert(n.results[0].children)
assert(len(n.results[0].children) == 7)
assert(isinstance(n.results[0].children[-1], QS))



#######
####### STRICT
#######

# \\ft empty
n = Parser('\\s1 THE SONG OF THE THREE HOLY CHILDREN\\f + \\fr 3:24  \\ft  \\ft \\+bk The Song of the Three Holy Children\\+bk* is an addition to \\+bk Daniel\\+bk* found in the Greek Septuagint but not found in the traditional Hebrew text of \\+bk Daniel\\+bk*. This portion is recognized as Deuterocanonical Scripture by the Roman Catholic, Greek Orthodox, and Russian Orthodox Churches. It is found inserted between Daniel 3:23 and Daniel 3:24 of the traditional Hebrew Bible. Here, the verses after 23 from the Hebrew Bible are numbered starting at 91 to make room for these verses.\\f*')
try:
    n.parse()
except USFMSyntaxError:
    pass
else:
    assert(False)
# needs to be either try-caught in client code, or change overall Parser strict


######
###### Going back and forth between SPAN LOOP and PARA LOOP
######



n = Parser('''\\ip \\bk The Wisdom of Jesus the Son of Sirach\\bk*, also called \\bk Ecclesiasticus\\bk*, is recognized as Deuterocanonical Scripture by the Roman Catholic, Greek Orthodox, and Russian Orthodox Churches. 
\\is1 The Prologue of the Wisdom of Jesus the Son of Sirach.''')
n.parse()
assert(n.results)
assert(len(n.results) == 2)
assert(isinstance(n.results[0], IP))
assert(isinstance(n.results[1], IS))
assert(n.results[0].children)
assert(len(n.results[0].children) == 4)
assert(isinstance(n.results[0].children[0], BK))
assert(n.results[0].children[0].get_value() == 'The Wisdom of Jesus the Son of Sirach')
assert(isinstance(n.results[0].children[1], Text))
assert(isinstance(n.results[0].children[2], BK))
assert(n.results[0].children[2].get_value() == 'Ecclesiasticus')
assert(isinstance(n.results[0].children[3], Text))

assert(n.results[1].children)
assert(len(n.results[1].children) == 1)
assert(isinstance(n.results[1].children[0], Text))
assert(n.results[1].get_value() == 'The Prologue of the Wisdom of Jesus the Son of Sirach.')








#######
###### 


# Verse get_text() shouldn't traverse chapter boundaries
n = Parser('''\\p
\\v 20 This ends \\w the|strong="H1732"\\w* \\w prayers|strong="H8605"\\w* \\w by|strong="H3615"\\w* \\w David|strong="H1732"\\w*, \\w the|strong="H1732"\\w* \\w son|strong="H1121"\\w* \\w of|strong="H1121"\\w* \\w Jesse|strong="H3448"\\w*. 
\\c 73  
\\ms1 BOOK 3
\\d A Psalm by Asaph.
\\q1
\\v 1  \\w Surely|strong="H0389"\\w* \\w God|strong="H0430"\\w*\\f + \\fr 73:1  \\ft The Hebrew word rendered “God” is “אֱלֹהִ֑ים” (Elohim).\\f* \\w is|strong="H0430"\\w* \\w good|strong="H2896"\\w* \\w to|strong="H3478"\\w* \\w Israel|strong="H3478"\\w*,''')
n.parse()
assert(n.results)
assert('Surely' not in n.results[0].get_text())


n = Parser('''\\q2 \\v 8 \\w Don’t|strong="H0408"\\w* \\w utterly|strong="H3966"\\w* \\w forsake|strong="H5800"\\w* \\w me|strong="H8104"\\w*. 
\\d BETH 
\\q1
\\v 9  \\w How|strong="H4100"\\w* \\w can|strong="H4100"\\w* \\w a|strong="H4100"\\w* \\w young|strong="H5288"\\w* \\w man|strong="H5288"\\w* \\w keep|strong="H8104"\\w* \\w his|strong="H8104"\\w* \\w way|strong="H0734"\\w* \\w pure|strong="H2135"\\w*?''')
n.parse()
assert(n.results)
assert('BETH' in n.results[2].children[0].get_text())


# ... but should traverse \q boundaries
n = Parser('''\\c 136   
\\q1
\\v 1  \\w Give|strong="H3034"\\w* \\w thanks|strong="H3034"\\w* \\w to|strong="H3068"\\w* \\w Yahweh|strong="H3068"\\w*, \\w for|strong="H3588"\\w* \\w he|strong="H3588"\\w* \\w is|strong="H3068"\\w* \\w good|strong="H2896"\\w*, 
\\q2 \\w for|strong="H3588"\\w* \\w his|strong="H3068"\\w* loving \\w kindness|strong="H2617"\\w* \\w endures|strong="H5769"\\w* \\w forever|strong="H5769"\\w*.''')
n.parse()
assert(n.results)
assert('endures' in n.results[0].get_verse(1).get_text())




# \\ft -> \\bk 
n = Parser('''\\s1 HOLY CHILDREN\\f + \\fr 3:24  \\ft \\+bk The Song of the Three Holy Children\\+bk* is\\ft''')
n.parse()
assert(n.results)

