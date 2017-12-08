""" FS helpers module. """

# system
import os

# fs
from fs.base import FS
from fs.osfs import OSFS

def assure_fs(path):
    """ Assure filesystem for each segment of the path.

    Args:
        path (str): Path

    Returns:
        fs
    """
    # possible separators
    separators = [u'/', u'\\']

    # find used separator
    separator = [sep for sep in separators if sep in path][0]

    # split path into parts using found separator
    path_parts = unicode(path).split(separator)

    def reduce_path(carry_fs, value):
        """ Reduce path by opening or creating each segment and returning the last. 

        Args:
            carry_fs (fs): Opened filesystem
            value (str): Next path segment

        Returns:
            fs
        """
        if not isinstance(carry_fs, FS):
            carry_fs = OSFS(carry_fs + separator)

        if not carry_fs.isdir(value):
            carry_fs.makedirs(value)

        # open next carry_fs
        next_carry_fs = OSFS(carry_fs.getsyspath(value))

        # close carry_fs
        carry_fs.close()

        return next_carry_fs

    return reduce(reduce_path, path_parts)

def main():
    assure_fs('../asdf')

if __name__ == '__main__':
    main()