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
from exrio import rename_dir, rename_file

class ArgumentParserError(Exception):
    """ Argument parser error. """

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

def main():
    # default layer map
    layer_map = {
        '^r$': 'R',
        '^g$': 'G',
        '^b$': 'B',
        '^a$': 'A',
    }

    # argument parser
    parser = ThrowingArgumentParser(description='Process EXRs.')

    # input path argument
    parser.add_argument('input', type=str, help='Path to an EXR file or a directory containing EXR files.')

    # output path argument
    parser.add_argument('output', type=str, help='Path to output directory.')

    # layer map argument
    parser.add_argument('map', type=str, help='Path to a JSON file containing the layers to rename. Use regular expression to find the name and replace it with a new name. Example: {}'.format(json.dumps(layer_map)))

    # number of threads
    parser.add_argument('--num_threads', type=int, help='Number of threads to use (Use all available threads by default).')

    # multithreading
    parser.add_argument('--multithreading', type=int, default=1, help='Use multithreading (default=1).')

    try:
        args = parser.parse_args()
    except Exception as error:
        print error

        parser.print_help()

        quit()

    # open output filesystem
    try:
        out_fs = OSFS(args.output)
    except CreateFailed:
        print 'Output {} does not exist.'.format(args.output)

        quit()

    # split map path
    dirname, basename = os.path.split(unicode(args.map))
    try:
        map_fs = OSFS(dirname)

        if map_fs.isfile(basename):
            with map_fs.open(basename) as file_handle:
                try:
                    layer_map = json.loads(file_handle.read())
                except Exception as error:
                    print error
    except CreateFailed:
        print 'Map {} does not exist.'.format(args.output)

        quit()

    # split input path
    dirname, basename = os.path.split(unicode(args.input))

    # open input filesystem
    try:
        in_fs = OSFS(dirname)

        if in_fs.isfile(basename):
            rename_file(in_fs.getsyspath(basename), out_fs.getsyspath(basename), layer_map)
        elif in_fs.isdir(basename):
            rename_dir(in_fs.opendir(basename), out_fs, layer_map, args.num_threads, bool(args.multithreading))
    except CreateFailed:
        print 'Input {} does not exist.'.format(args.input)

        quit()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    main()