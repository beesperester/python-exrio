""" exrio custom exceptions module. """

class NoExrFileException(Exception):
    """ No EXR file exception. """

class SameDirectoryException(Exception):
    """ Same directory exception. """

class SameFileException(Exception):
    """ Same file exception. """

class LayerMapEmptyException(Exception):
    """ Layermap is empty exception. """