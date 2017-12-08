""" List helpers module. """

def sort_rgba(channels):
    """ Sort channels by rgba.

    Args:
        channels (list): List of channels to sort

    Returns:
        list
    """
    order = {
        0: '.red',
        1: '.green',
        2: '.blue',
        3: '.alpha'
    }

    sorted_channels = []

    for index, value in order.iteritems():
        for channel in channels:
            if channel.endswith(value):
                sorted_channels.insert(index, channel)

    if sorted_channels:
        return sorted_channels

    return channels
