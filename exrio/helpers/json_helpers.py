""" Json helpers module. """

# system
import json

def is_jsonable(value):
    """ Test if a value can be json serialized.

    Args:
        value (mixed): Value

    Returns:
        bool
    """
    try:
        json.dumps(value)
        return True
    except:
        return False

def filter_jsonable(value, callback=None):
    """ Filter input if it is not jsonable.

    Args:
        value (mixed): Value

    Returns:
        mixed
    """
    if is_jsonable(value):
        return value

    if isinstance(value, list):
        return [filter_jsonable(item, callback) for item in value]

    if isinstance(value, dict):
        return {item_key: filter_jsonable(item_value, callback) for item_key, item_value in value.iteritems()}

    if hasattr(callback, '__call__'):
        return callback(value)
