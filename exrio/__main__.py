""" Main python module. """

# system
import argparse
import json
import os
import sys

from multiprocessing import freeze_support

# filesystem
from fs.osfs import OSFS
from fs.errors import CreateFailed

# exrio
from exrio.rechannel import rechannel_dir, rechannel_file
from exrio.preview import preview_dir, preview_file
from exrio.inspect import inspect_dir, inspect_file
from exrio import console

# helpers
from exrio.helpers.dict_helpers import dict_to_namedtuple
from exrio.helpers.fs_helpers import assure_fs

# overrides

try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen

# exceptions

class ArgumentParserError(Exception):
    """ Argument parser error. """

# classes

class ThrowingArgumentParser(argparse.ArgumentParser):
    """ Custom argument parser class. """

    def error(self, message):
        raise ArgumentParserError(message)

# methods

def apply_multiprocessing_arguments(parser):
    # number of threads
    parser.add_argument('--num_threads', type=int, help='Number of threads to use (Use all available threads by default).')

    # multithreading
    parser.add_argument('--multithreading', type=int, default=1, help='Use multithreading (default=1).')

def apply_input_output_arguments(parser):
    # input path argument
    parser.add_argument('input', default=os.getcwd(), type=str, help='Path to an EXR file or a directory containing EXR files.')

    # output path argument
    parser.add_argument('output', type=str, help='Path to output directory.')

    # prefix
    parser.add_argument('--prefix', type=str, help='Prefix output files.')

def handle_arguments():
    """ Commandline arguments entrypoint. """

    # default layer map
    layer_map = {
        '^(?P<layer>r)$': 'R',
        '^(?P<layer>g)$': 'G',
        '^(?P<layer>b)$': 'B',
        '^(?P<layer>a)$': 'A',
        '(?P<layer>diffuse)\.(?P<channel>\S+)': 'diffuse'
    }

    # argument parser
    parser = ThrowingArgumentParser(description='Commandline tool for processing .exr files. Create previews or rename layers and channels.', prog='exrio')

    subparsers = parser.add_subparsers(help='Submodule commands.', dest='module')

    # create rechannel subparser
    rechannel_parser = subparsers.add_parser('rechannel', help='Rename layers and channels in EXR files and directories containing EXR files.')    

    # example
    rechannel_parser.add_argument('--example', action='store_true', help='Create example map at current working directory.')

    # extra step to check if an example map should be created
    try:
        args = parser.parse_args()

        if args.module == 'rechannel':
            if args.example:
                cwd_fs = OSFS(u'.')

                with cwd_fs.open(u'example.json', mode='w') as file_handle:
                    file_handle.write(unicode(json.dumps(layer_map, indent=2)))
                
                return
    except ArgumentParserError as error:
        pass

    apply_input_output_arguments(rechannel_parser)

    # layer map argument
    rechannel_parser.add_argument('map', type=str, help='Path to a JSON file containing the layers to rename. Use regular expression to find the name and replace it with a new name. Example: {}'.format(json.dumps(layer_map)))

    apply_multiprocessing_arguments(rechannel_parser)

    # create preview subparser
    preview_parser = subparsers.add_parser('preview', help='Create previews for EXR files and directories containing EXR files.')

    apply_input_output_arguments(preview_parser)

    apply_multiprocessing_arguments(preview_parser)

    # layer
    preview_parser.add_argument('--layer', type=str, nargs='+', help='Select layer to preview (default=rgb).')

    # create inspect subparser
    inspect_parser = subparsers.add_parser('inspect', help='Inspect EXR files or a directory containing EXR files.')

    # input path argument
    inspect_parser.add_argument('input', type=str, help='Path to an EXR file or a directory containing EXR files.')

    try:
        args = parser.parse_args()
    except ArgumentParserError as error:
        console.error(error.message)

        parser.print_help()

        return
    except Exception as error:
        console.error(error.message)

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
        'prefix': None,
        'map': None,
        'num_threads': None,
        'multithreading': 1
    }

    default_args.update(kwargs)

    args = dict_to_namedtuple(default_args)

    # open output filesystem
    out_fs = assure_fs(args.output)

    # split map path
    dirname, basename = os.path.split(unicode(args.map))
    try:
        map_fs = OSFS(dirname)

        if map_fs.isfile(basename):
            with map_fs.open(basename) as file_handle:
                try:
                    layer_map = json.loads(file_handle.read())
                except Exception as error:
                    console.error(error)

                    return
        else:
            console.error('Map {} does not exist.'.format(args.map))

            return
    except CreateFailed:
        console.error('Map parent directory {} does not exist.'.format(args.map))

        return

    # split input path
    dirname, basename = os.path.split(unicode(args.input))

    # open input filesystem
    try:
        in_fs = OSFS(dirname)

        if in_fs.isfile(basename):
            # prepend prefix to basename
            if args.prefix:
                basename = args.prefix + basename

            rechannel_file(in_fs.getsyspath(basename), out_fs.getsyspath(basename), layer_map)
        elif in_fs.isdir(basename):
            rechannel_dir(in_fs.opendir(basename), out_fs, layer_map, args.num_threads, bool(args.multithreading), prefix=args.prefix)
    except CreateFailed:
        console.error('Input {} does not exist.'.format(args.input))

        return

def handle_preview(**kwargs):
    """ Handle preview actions.

    Args:
        **kwargs (dict): Arguments
    """
    default_args = {
        'input': None,
        'output': None,
        'prefix': None,
        'layer': None,
        'num_threads': None,
        'multithreading': 1
    }

    default_args.update(kwargs)

    args = dict_to_namedtuple(default_args)

    # open output filesystem
    out_fs = assure_fs(args.output)

    # join layer
    layer = None

    if args.layer:
        layer = ' '.join(args.layer)

    # split input path
    dirname, basename = os.path.split(unicode(args.input))

    # open input filesystem
    try:
        in_fs = OSFS(dirname)

        if in_fs.isfile(basename):
            filename, extension = os.path.splitext(basename)

            # prepend prefix to filename
            if args.prefix:
                filename = args.prefix + filename

            out_name = unicode(filename + '.jpg')

            preview_file(in_fs.getsyspath(basename), out_fs.getsyspath(out_name), layer)
        elif in_fs.isdir(basename):
            preview_dir(in_fs.opendir(basename), out_fs, args.num_threads, bool(args.multithreading), prefix=args.prefix, layer=layer)
    except CreateFailed:
        console.error('Input {} does not exist.'.format(args.input))

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
        console.error('Input {} does not exist.'.format(args.input))

        return

if __name__ == '__main__':
    freeze_support()

    handle_arguments()
