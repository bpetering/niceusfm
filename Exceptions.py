# -*- coding: UTF-8 -*-

class USFMException(Exception):
    """Base class for exceptions"""

class ElementNoValueError(USFMException):
    """This element does not have a value"""

class InvalidElementError(USFMException):
    """This element is not valid in some way"""

class InvalidMarkerError(USFMException):
    """This marker is not valid in some way"""



class ParserError(USFMException):
    """Parser error"""

class USFMSyntaxError(ParserError):
    """"""

class NoTokenError(ParserError):
    """Token requested but doesn't exist"""

class NonExistentMarkerError(ParserError):
    """This marker doesn't exist in USFM"""

class InvalidAttributeError(ParserError):
    """This attribute contains invalid content"""

