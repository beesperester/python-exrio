""" Dict helper module. """

# system
from collections import namedtuple

def dict_to_namedtuple(dictionary):
    """ Convert dict to namedtuple.

    Args:
        dictionary (dict): Dict to convert

    Returns:
        namedtuple
    """
    return namedtuple('GenericDict', dictionary.keys())(**dictionary)
