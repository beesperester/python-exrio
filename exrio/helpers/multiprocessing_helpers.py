""" Multiprocessing helpers module. """

# system
import os
import time

from multiprocessing import Pool

# exrio
from exrio import console

def _task_worker(args):
    """ Run args if is callable.

    Args:
        args (list): Arguments
    """
    if len(args) > 0:
        callback = args[0]

        callback_args = []

        if len(args) > 1:
            callback_args = args[1:]

        if hasattr(callback, '__call__'):
            callback(*callback_args)

def run(tasks, num_threads=None, multiprocessing=True):
    """ Run tasks with num_threads if multiprocessing.

    Args:
        tasks (list): Tasks to process
        num_threads (int): Number of threads
        multiprocessing (bool): Use multiprocessing
    """
    if not num_threads:
        num_threads = int(os.environ["NUMBER_OF_PROCESSORS"])

    # only spawn maxium of len(tasks) threads if num_threads larger than len(tasks)
    if num_threads > len(tasks):
        num_threads = len(tasks)

    console.debug('Number of threads for multiprocessing: {}'.format(num_threads))

    if multiprocessing:
        # run tasks in parallel
        pool = Pool(processes=num_threads)

        pool.map(_task_worker, tasks)
    else:
        # run tasks in order
        for task in tasks:
            _task_worker(task)