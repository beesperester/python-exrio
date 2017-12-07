""" Main python module. """

# system
import argparse
import json
import logging
import os

# filesystem
from fs.osfs import OSFS
from fs.errors import CreateFailed

# exrio
from exrio.rechannel import rechannel_dir, rechannel_file
from exrio.preview import preview_dir, preview_file
from exrio.inspect import inspect_dir, inspect_file

# helpers
from exrio.helpers.dict_helpers import dict_to_namedtuple

class ArgumentParserError(Exception):
    """ Argument parser error. """

class ThrowingArgumentParser(argparse.ArgumentParser):
    """ Custom argument parser class. """

    def error(self, message):
        raise ArgumentParserError(message)

def handle_arguments():
    """ Commandline arguments entrypoint. """

    # argument parser
    parser = ThrowingArgumentParser(description='Commandline tool for processing .exr files. Create previews or rename layers and channels.', prog='exrio')

    subparsers = parser.add_subparsers(help='Submodule commands.', dest='module')

    # create rechannel subparser
    rechannel_parser = subparsers.add_parser('rechannel', help='Rename layers and channels in EXR files and directories containing EXR files.')

    # input path argument
    rechannel_parser.add_argument('input', type=str, help='Path to an EXR file or a directory containing EXR files.')

    # output path argument
    rechannel_parser.add_argument('output', type=str, help='Path to output directory.')

    # layer map argument
    # default layer map
    layer_map = {
        '^(?P<layer>r)$': 'R',
        '^(?P<layer>g)$': 'G',
        '^(?P<layer>b)$': 'B',
        '^(?P<layer>a)$': 'A',
        '(?P<layer>diffuse)\.(?P<channel>\S+)': 'diffuse'
    }

    rechannel_parser.add_argument('map', type=str, help='Path to a JSON file containing the layers to rename. Use regular expression to find the name and replace it with a new name. Example: {}'.format(json.dumps(layer_map)))

    # number of threads
    rechannel_parser.add_argument('--num_threads', type=int, help='Number of threads to use (Use all available threads by default).')

    # multithreading
    rechannel_parser.add_argument('--multithreading', type=int, default=1, help='Use multithreading (default=1).')

    # create preview subparser
    preview_parser = subparsers.add_parser('preview', help='Create previews for EXR files and directories containing EXR files.')

    # input path argument
    preview_parser.add_argument('input', type=str, help='Path to an EXR file or a directory containing EXR files.')

    # output path argument
    preview_parser.add_argument('output', type=str, help='Path to output directory.')

    # number of threads
    preview_parser.add_argument('--num_threads', type=int, help='Number of threads to use (Use all available threads by default).')

    # multithreading
    preview_parser.add_argument('--multithreading', type=int, default=1, help='Use multithreading (default=1).')

    # create inspect subparser
    inspect_parser = subparsers.add_parser('inspect', help='Inspect EXR files or a directory containing EXR files.')

    # input path argument
    inspect_parser.add_argument('input', type=str, help='Path to an EXR file or a directory containing EXR files.')

    try:
        args = parser.parse_args()
    except ArgumentParserError as error:
        print error

        parser.print_help()

        return

    if args.module == 'rechannel':
        handle_rechannel(**vars(args))
    elif args.module == 'preview':
        handle_preview(**vars(args))
    elif args.module == 'inspect':
        handle_inspect(**vars(args))

def handle_rechannel(**kwargs):
    """ Handle rechannel actions.

    Args:
        **kwargs (dict): Arguments
    """
    default_args = {
        'input': None,
        'output': None,
        'map': None,
        'num_threads': None,
        'multithreading': 1
    }

    default_args.update(kwargs)

    args = dict_to_namedtuple(default_args)

    # open output filesystem
    try:
        out_fs = OSFS(args.output)
    except CreateFailed:
        print 'Output {} does not exist.'.format(args.output)

        return

    # split map path
    dirname, basename = os.path.split(unicode(args.map))
    try:
        map_fs = OSFS(dirname)

        if map_fs.isfile(basename):
            with map_fs.open(basename) as file_handle:
                try:
                    layer_map = json.loads(file_handle.read())
                except Exception as error:
                    logging.error(error)

                    return
    except CreateFailed:
        print 'Map {} does not exist.'.format(args.output)

        return

    # split input path
    dirname, basename = os.path.split(unicode(args.input))

    # open input filesystem
    try:
        in_fs = OSFS(dirname)

        if in_fs.isfile(basename):
            rechannel_file(in_fs.getsyspath(basename), out_fs.getsyspath(basename), layer_map)
        elif in_fs.isdir(basename):
            rechannel_dir(in_fs.opendir(basename), out_fs, layer_map, args.num_threads, bool(args.multithreading))
    except CreateFailed:
        print 'Input {} does not exist.'.format(args.input)

        return

def handle_preview(**kwargs):
    """ Handle preview actions.

    Args:
        **kwargs (dict): Arguments
    """
    default_args = {
        'input': None,
        'output': None,
        'num_threads': None,
        'multithreading': 1
    }

    default_args.update(kwargs)

    args = dict_to_namedtuple(default_args)

    # open output filesystem
    try:
        out_fs = OSFS(args.output)
    except CreateFailed:
        print 'Output {} does not exist.'.format(args.output)

        return

    # split input path
    dirname, basename = os.path.split(unicode(args.input))

    # open input filesystem
    try:
        in_fs = OSFS(dirname)

        if in_fs.isfile(basename):
            filename, extension = os.path.splitext(basename)

            out_name = unicode(filename + '.jpg')

            preview_file(in_fs.getsyspath(basename), out_fs.getsyspath(out_name))
        elif in_fs.isdir(basename):
            preview_dir(in_fs.opendir(basename), out_fs, args.num_threads, bool(args.multithreading))
    except CreateFailed:
        print 'Input {} does not exist.'.format(args.input)'

        return

def handle_inspect(**kwargs):
    """ Handle inspect actions.

    Args:
        **kwargs (dict): Arguments
    """
    default_args = {
        'input': None
    }

    default_args.update(kwargs)

    args = dict_to_namedtuple(default_args)

    # split input path
    dirname, basename = os.path.split(unicode(args.input))

    # open input filesystem
    try:
        in_fs = OSFS(dirname)

        if in_fs.isfile(basename):
            inspect_file(in_fs.getsyspath(basename))
        elif in_fs.isdir(basename):
            inspect_dir(in_fs.opendir(basename))
    except CreateFailed:
        print 'Input {} does not exist.'.format(args.input)

        return

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    handle_arguments()
