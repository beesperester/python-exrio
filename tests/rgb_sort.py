""" RGB sort test module. """

from exrio.helpers.list_helpers import sort_rgba

channels = [
    'Position (World).blue',
    'Position (World).alpha',
    'Position (World).green',
    'Position (World).red',
]

channels = sort_rgba(channels)

print channels