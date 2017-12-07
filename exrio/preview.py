""" Preview exr module. """

# system
import os
import time

from multiprocessing import Pool, freeze_support

# image manipulation
import OpenEXR
import Imath
import Image

# exceptions
from exrio.exrio_exceptions import NoExrFileException, SameFileException

def preview_file(in_path, out_path):
    """ TODO: add docstring.

    Args:
        in_path (str): File to read
        out_path (str): File to write

    Raises:
        NoExrFileException
    """
    print 'Started preview of {out_path}.'.format(out_path=out_path)

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

    print 'Finished preview for {out_path} ({duration}s).'.format(out_path=out_path, duration=duration)

def preview_worker(args):
    """ TODO: add docstring. """

    preview_file(*args)

def preview_files(files, out_fs, num_threads=None, multithreading=True):
    """ TODO: add docstring.

    Args:
        files (list): List of exr files
        out_fs (fs): Output filesystem
        num_threads (int): Number of threads to use
        multithreading (bool): Use multithreading

    Raises:
        SameFileException
    """
    freeze_support()
    
    print 'Started preview of {} files.'.format(len(files))

    if not num_threads:
        num_threads = int(os.environ["NUMBER_OF_PROCESSORS"])

    tasks = []

    for file_path in files:
        dirname, basename = os.path.split(file_path)

        filename, extension = os.path.splitext(basename)

        out_name = unicode(filename + '.jpg')

        # get out_path
        out_path = out_fs.getsyspath(out_name)

        tasks.append((file_path, out_path))

    if multithreading:
        # run tasks in parallel
        pool = Pool(processes=num_threads)

        pool.map(preview_worker, tasks)
    else:
        # run tasks in order
        for task in tasks:
            preview_worker(task)

    print 'Finished preview of {} files.'.format(len(files))

def preview_dir(in_fs, out_fs, num_threads=None, multithreading=True):
    """ TODO: add docstring.

    Args:
        in_fs (fs): Input filesystem
        out_fs (fs): Output filesystem
        num_threads (int): Number of threads to use
        multithreading (bool): Use multithreading
    """

    files = []

    for file_name in in_fs.walk.files(filter=['*.exr']):
        files.append(in_fs.getsyspath(file_name))

    return preview_files(files, out_fs, num_threads, multithreading)
