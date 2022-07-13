# -*- coding: UTF-8 -*-

class NumberedElement:
    
    def __init__(self, number=1):
        if isinstance(number, str):
            self.number = int(number)
        elif isinstance(number, int):
            self.number = number
        else:
            self.number = 1         
        if self.number < 1:
            self.number = 1
        self._repr_children = True

    def __repr__(self):
        out = "{}{}(start={}, end={}, marker='{}', number={}".format(
            '    ' * self._depth,
            self.__class__.__name__,
            self.start, 
            self.end,
            self.marker,
            self.number
        )   
        if self.children and self._repr_children:
            out += ", children=[\n"
            for child in self.children:
                out += str(child) + ',\n'
            out += '    ' * self._depth + '])'
        else:
            out += ')' 
        return out 
