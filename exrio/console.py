""" Console output module. """

def _output_args(*args):
    print ' '.join([repr(arg).strip('\'') for arg in args])

def error(*args):
    _output_args('ERROR:', *args)

def info(*args):
    _output_args('INFO:', *args)

def warning(*args):
    _output_args('WARNING:', *args)

def debug(*args):
    _output_args('DEBUG:', *args)