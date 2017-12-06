""" Main python module. """

# system
import copy
import json
import logging
import os
import re
import time

from Queue import Queue, Empty
from threading import Thread

# exr
import OpenEXR

class NoExrFileException(Exception):
    """ No EXR file exception. """

class SameDirectoryException(Exception):
    """ Same directory exception. """

class SameFileException(Exception):
    """ Same file exception. """

class LayerMapEmptyException(Exception):
    """ Layermap is empty exception. """

def rename_layer_name(layer_name, replacement_name, replacement_format='{layer_name}.{channel_name}'):
    """ Rename layer with replacement.

    Args:
        layer_name (str): Layer name
        replacement_name (str): Replacement name
        replacement_format (str): Replacement format

    Returns:
        str
    """
    split_channel = layer_name.split('.')
                
    # create renamed layer name
    if len(split_channel) > 1:
        renamed_layer_name = replacement_format.format(layer_name=replacement_name, channel_name=split_channel[-1])
    else:
        renamed_layer_name = replacement_name

    return renamed_layer_name

def rename_channels(in_path, out_path, layer_map=None, rename_method=None):
    """ Rename layers of exr file at in_path by replacing layer names via regular expression provided by layer_map and storing a new exr file at out_path.

    Args:
        in_path (str): File to read
        out_path (str): File to write
        layer_map (dict): Regular expression / replacement name pairs
        rename_method (method): Method for creating the new layer name

    Raises:
        NoExrFileException
    """
    logging.info('Start rename of {out_path}.'.format(out_path=out_path))

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
            if re.search(pattern, layer_name, flags=re.IGNORECASE):
                if not hasattr(rename_method, '__call__'):
                    rename_method = rename_layer_name
                    
                renamed_layer_name = rename_method(layer_name, replacement_name)

                # insert renamed channel into header with old channel value
                out_exr_header['channels'].update({
                    renamed_layer_name: value
                })

                # store renamed layer with data
                matched_layers[renamed_layer_name] = in_exr_file.channel(layer_name)

    out_exr_file = OpenEXR.OutputFile(out_path, out_exr_header)

    # copy matched layers
    if matched_layers:
        out_exr_file.writePixels(matched_layers)

    out_exr_file.close()

    # stop time
    time_stop = time()

    # duration
    duration = time_stop - time_start

    logging.info('Renamed {num_channels} channels of {out_path} ({duration}s).'.format(num_channels=len(matched_layers.keys()), out_path=out_path, duration=duration))

def rename_files(files, out_fs, layer_map=None, rename_method=None, num_threads=8):
    """ Rename layers in list of exr files and store at out_fs.

    Args:
        files (list): List of exr files
        out_fs (fs): Output filesystem
        layer_map (dict): regular expression / replacement name pairs
        rename_method (method): Method for creating the new layer name

    Raises:
        SameFileException
    """
    logging.info('Started renaming of {} files.'.format(len(files)))

    queue = Queue()

    def worker():
        while True:
            try:
                callback = queue.get()
                
                if hasattr(callback, '__call__'):
                    callback()
                
                queue.task_done()
            except Empty:
                logging.warning('Queue is empty')
                break

    for index in range(0, num_threads):
        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()

    logging.info('Started {} threads.'.format(num_threads))

    for file_path in files:
        dirname, basename = os.path.split(file_path)

        # get out_path
        out_path = out_fs.getsyspath(unicode(basename))

        # check if file_path and out_path are not identical (Don't override input)
        if file_path == out_path:
            raise SameFileException(out_path)

        # rename_channels(file_path, out_path, layer_map, rename_method)

        queue.put(lambda: rename_channels(file_path, out_path, layer_map, rename_method))

    queue.join()

    logging.info('Finished renaming of {} files.'.format(len(files)))

def rename_dir(in_fs, out_fs, layer_map=None, rename_method=None, num_threads=8):
    """ Rename exr files in in_fs.

    Args:
        in_fs (fs): Input filesystem
        out_fs (fs): Output filesystem
        layer_map (dict): regular expression / replacement name pairs
        rename_method (method): Method for creating the new layer name
    """

    files = []

    for file_name in in_fs.walk.files(filter=['*.exr']):
        files.append(in_fs.getsyspath(file_name))

    return rename_files(files, out_fs, layer_map, rename_method, num_threads)