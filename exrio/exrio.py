""" Module of exr file operations. """

# system
import copy
import json
import logging
import os
import re
import time

from multiprocessing import Pool

# exr
import OpenEXR

# exceptions

class NoExrFileException(Exception):
    """ No EXR file exception. """

class SameDirectoryException(Exception):
    """ Same directory exception. """

class SameFileException(Exception):
    """ Same file exception. """

class LayerMapEmptyException(Exception):
    """ Layermap is empty exception. """

# methods

def rename_file(in_path, out_path, layer_map=None):
    """ Rename layers of exr file at in_path by replacing layer names via regular expression provided by layer_map and storing a new exr file at out_path.

    Args:
        in_path (str): File to read
        out_path (str): File to write
        layer_map (dict): Regular expression / replacement name pairs

    Raises:
        NoExrFileException
    """
    logging.info('Start rename of {out_path}.'.format(out_path=out_path))

    if in_path == out_path:
        raise SameFileException(out_path)

    # start time
    time_start = time.time()

    if not layer_map:
        layer_map = {}

    if not OpenEXR.isOpenExrFile(in_path):
        raise NoExrFileException(in_path)

    # open exr file
    in_exr_file = OpenEXR.InputFile(in_path)

    # get open exr header
    in_exr_header = in_exr_file.header()

    # create new copy from header
    out_exr_header = copy.deepcopy(in_exr_header)

    # reset channels
    out_exr_header['channels'] = {}

    # empty dict for matched layers
    matched_layers = {}

    for layer_name, value in in_exr_header['channels'].iteritems():
        for pattern, replacement_name in layer_map.iteritems():
            matches = re.search(r'{}'.format(pattern), layer_name, flags=re.IGNORECASE)

            if matches:
                match_data = matches.groupdict()

                if 'channel' in match_data.keys():
                    out_channel_name = replacement_name + '.' + match_data['channel']
                else:
                    out_channel_name = replacement_name

                # insert renamed channel into header with old channel value
                out_exr_header['channels'].update({
                    out_channel_name: value
                })

                # store renamed layer with data
                matched_layers[out_channel_name] = in_exr_file.channel(layer_name)

    out_exr_file = OpenEXR.OutputFile(out_path, out_exr_header)

    # copy matched layers
    if matched_layers:
        out_exr_file.writePixels(matched_layers)

    out_exr_file.close()

    # stop time
    time_stop = time.time()

    # duration
    duration = time_stop - time_start

    logging.info('Renamed {num_channels} channels of {out_path} ({duration}s).'.format(num_channels=len(matched_layers.keys()), out_path=out_path, duration=duration))

def rename_worker(args):
    rename_file(*args)

def rename_files(files, out_fs, layer_map=None, num_threads=None, multithreading=True):
    """ Rename layers in list of exr files and store at out_fs.

    Args:
        files (list): List of exr files
        out_fs (fs): Output filesystem
        layer_map (dict): regular expression / replacement name pairs
        num_threads (int): Number of threads to use
        multithreading (bool): Use multithreading

    Raises:
        SameFileException
    """        
    logging.info('Started renaming of {} files.'.format(len(files)))

    if not num_threads:
        num_threads = int(os.environ["NUMBER_OF_PROCESSORS"])

    tasks = []

    for file_path in files:
        dirname, basename = os.path.split(file_path)

        # get out_path
        out_path = out_fs.getsyspath(unicode(basename))

        tasks.append((file_path, out_path, layer_map))

    if multithreading:
        # run tasks in parallel
        pool = Pool(processes=num_threads)

        pool.map(rename_worker, tasks)
    else:
        # run tasks in order
        for task in tasks:
            rename_worker(task)

    logging.info('Finished renaming of {} files.'.format(len(files)))

def rename_dir(in_fs, out_fs, layer_map=None, num_threads=None, multithreading=True):
    """ Rename exr files in in_fs.

    Args:
        in_fs (fs): Input filesystem
        out_fs (fs): Output filesystem
        layer_map (dict): regular expression / replacement name pairs
        num_threads (int): Number of threads to use
        multithreading (bool): Use multithreading
    """

    files = []

    for file_name in in_fs.walk.files(filter=['*.exr']):
        files.append(in_fs.getsyspath(file_name))

    return rename_files(files, out_fs, layer_map, num_threads, multithreading)
