""" Preview exr module. """

# system
import json
import time

# image manipulation
import OpenEXR

# exceptions
from exrio.exrio_exceptions import NoExrFileException, SameFileException

# helpers
from exrio.helpers.json_helpers import is_jsonable, filter_jsonable
from exrio.helpers.multiprocessing_helpers import run

def inspect_file(in_path):
    """ TODO: add docstring.

    Args:
        in_path (str): File to read

    Raises:
        NoExrFileException
    """
    print 'Started inspect of {in_path}.'.format(in_path=in_path)

    # start time
    time_start = time.time()

    if not OpenEXR.isOpenExrFile(in_path):
        raise NoExrFileException(in_path)

    # open exr file
    in_exr_file = OpenEXR.InputFile(in_path)

    # get open exr header
    in_exr_header = in_exr_file.header()

    # printable_exr_header = {key: value for key, filter_jsonable(value) in in_exr_header.iteritems()}

    def catch_value(value):
        """ Catch non-jsonable values.

        Args:
            value (mixed): Value

        Returns:
            mixed
        """
        # if isinstance(value, Imath.Box2i):
        return repr(value)

    print json.dumps(filter_jsonable(in_exr_header, catch_value), indent=4)

    # stop time
    time_stop = time.time()

    # duration
    duration = round(time_stop - time_start)

    print 'Finished inspect for {in_path} ({duration}s).'.format(in_path=in_path, duration=duration)

def inspect_files(files):
    """ TODO: add docstring.

    Args:
        files (list): List of exr files
    """
    print 'Started inspect of {} files.'.format(len(files))

    tasks = []

    for file_path in files:
        tasks.append((inspect_file, file_path))

    run(tasks, None, False)

    print 'Finished inspect of {} files.'.format(len(files))

def inspect_dir(in_fs):
    """ TODO: add docstring.

    Args:
        in_fs (fs): Input filesystem
    """

    files = []

    for file_name in in_fs.walk.files(filter=['*.exr']):
        files.append(in_fs.getsyspath(file_name))

    return inspect_files(files)