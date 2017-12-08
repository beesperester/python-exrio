""" Preview exr module. """

# system
import os
import time

# image manipulation
import OpenEXR
import Imath
import Image

# exceptions
from exrio.exrio_exceptions import NoExrFileException, SameFileException

# helpers
from exrio.helpers.multiprocessing_helpers import run

# exrio
from exrio import console

def preview_file(in_path, out_path):
    """ Create preview of exr files by normalizing the color range to 8bit.

    Args:
        in_path (str): File to read
        out_path (str): File to write

    Raises:
        NoExrFileException
    """
    console.info('Started preview of {in_path}.'.format(in_path=os.path.basename(in_path)))

    if in_path == out_path:
        raise SameFileException(out_path)

    # start time
    time_start = time.time()

    if not OpenEXR.isOpenExrFile(in_path):
        raise NoExrFileException(in_path)

    # open exr file
    in_exr_file = OpenEXR.InputFile(in_path)

    # get open exr header
    in_exr_header = in_exr_file.header()

    pixel_type = Imath.PixelType(Imath.PixelType.FLOAT)
    data_window = in_exr_header['dataWindow']
    size = (data_window.max.x - data_window.min.x + 1, data_window.max.y - data_window.min.y + 1)

    rgbf = [Image.fromstring("F", size, in_exr_file.channel(c, pixel_type)) for c in "RGB"]

    extrema = [im.getextrema() for im in rgbf]
    darkest = min([lo for (lo,hi) in extrema])
    lighest = max([hi for (lo,hi) in extrema])
    scale = 255 / (lighest - darkest)

    def normalize_0_255(value):
        """ Normalize value.

        Args:
            value (float): Value to normalize
        """
        return (value * scale) + darkest

    rgb8 = [im.point(normalize_0_255).convert("L") for im in rgbf]

    Image.merge("RGB", rgb8).save(out_path)

    # stop time
    time_stop = time.time()

    # duration
    duration = round(time_stop - time_start)

    console.info('Finished preview for {out_path} ({duration}s).'.format(out_path=os.path.basename(out_path), duration=duration))

def preview_files(files, out_fs, num_threads=None, multiprocessing=True, **kwargs):
    """ Create previews for a list of files and use multiprocessing.

    Args:
        files (list): List of exr files
        out_fs (fs): Output filesystem
        num_threads (int): Number of threads to use
        multiprocessing (bool): Use multiprocessing

    Raises:
        SameFileException
    """
    console.info('Started preview of {} files.'.format(len(files)))

    tasks = []

    for file_path in files:
        dirname, basename = os.path.split(file_path)

        filename, extension = os.path.splitext(basename)

        # prepend prefix to filename
        if 'prefix' in kwargs and kwargs['prefix']:
            filename = kwargs['prefix'] + filename

        out_name = unicode(filename + '.jpg')

        # get out_path
        out_path = out_fs.getsyspath(out_name)

        tasks.append((preview_file, file_path, out_path))

    run(tasks, num_threads, multiprocessing)

    console.info('Finished preview of {} files.'.format(len(files)))

def preview_dir(in_fs, out_fs, num_threads=None, multithreading=True, **kwargs):
    """ Create list of exr files in directory and create previews.

    Args:
        in_fs (fs): Input filesystem
        out_fs (fs): Output filesystem
        num_threads (int): Number of threads to use
        multithreading (bool): Use multithreading
    """

    files = []

    for file_name in in_fs.walk.files(filter=['*.exr']):
        files.append(in_fs.getsyspath(file_name))

    return preview_files(files, out_fs, num_threads, multithreading, **kwargs)
