# -*- coding: UTF-8 -*-

import collections          
import re

# prefer this to typing.NamedTuple for now
class Token(collections.namedtuple('Token', ['type', 'value', 'start', 'end'])):

    __slots__ = ()
    # can @property to define new method

    TYPE_MARKER_START = 1
    TYPE_MARKER_END = 2
    TYPE_TEXT = 3
    TYPE_ATTRIBUTE = 4
    TYPE_SPACE = 5
    TYPE_NEWLINE = 6

    def const_to_name(self, const):
        v = dict(vars(type(self)))

        del_keys = [x for x in v.keys() if x.startswith('_') or not re.match(r'[A-Z_]+', str(x))]
        for k in del_keys:
            del v[k]

        const_types_by_value = dict(zip(v.values(), v.keys()))
        if const in const_types_by_value:
            return const_types_by_value[const]
        else:
            raise KeyError("constant with value {} doesn't exist in Token class".format(const))

    def value_for_output(self, value):
        value = value.replace('\\', '\\\\')
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        value = value.replace('\t', '\\t')
        return value
    
    def __repr__(self):
        return '{}(type={}, value=\'{}\', start={}, end={})'.format(
            self.__class__.__name__,
            'Token.' + self.const_to_name(self.type),
            self.value_for_output(self.value),
            self.start,
            self.end
        )

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
            and self.start == other.start \
            and self.end == other.end \
            and self.type == other.type \
            and self.value == other.value
