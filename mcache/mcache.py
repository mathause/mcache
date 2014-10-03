#! /usr/bin/env python


# Mathias Hauser @ IAC ETHZ; 05.2014

# wrapper for joblib Memory cache function


import sys
import errno
import os
import inspect
import warnings

from joblib import Memory

# TODO:
# - save in __pycache__ folder instead of .mcache?
# - make a .mcache folder for every folder instead of a root?
#   could be easier to use; harder to get rid of


def cache(verbose=2):
    """replacement for Memory.cache function with automatic folder 
        handling initiate a .mcache folder by running mcache init [path]

        mcache creates a folder for each calling function

    """

    # get path of calling function
    path, filename = get_caller()

    # find if mcache folder exists above the path of the caller
    root = find_mcache_folder(path)

    # eliminate root from the caller path, remove '/' at begining of path
    path = path.replace(root, '').lstrip(os.sep)

    # create unique filename
    mcache_folder = os.path.join(root, '.mcache', path, filename)

    makedir(mcache_folder)

    # initiate Memory class
    memory = Memory(cachedir=mcache_folder, verbose=verbose)

    # return the decorator function
    return memory.cache


def get_caller():
    """returns path and filename of function that called 'cache()'"""

    # this could be brittle

    # get the stack -> 0 is self, 1 is cache 2 is fcn that called cache
    caller = inspect.stack()[2][1]
    path, filename = os.path.split(caller)

    # sometimes stack only returns the filename w/o path
    # try to get it from filename
    if path is '':
        path = os.path.dirname(os.path.realpath(filename))

    # make sure it is a .py file -> necessary?
    if len(filename) < 3 or filename[-3:] != '.py':
        raise Exception('file: %s is not a "*.py" file (at %s)'
                        % (filename, path))
    return path, filename


def find_mcache_folder(path, folder='.mcache'):
    """search folder tree for a .mcache folder"""

    # make sure we do not get caught up in an infinite loop
    if not os.path.isdir(path):
        raise Exception("an ivalid path ('%s') was passed to look for "
                        "an mcache_folder" % path)

    # calling ./mcache.py from the cmdline returns '.' as path
    if path == '.':
        warnings.warn("mcache: find_mcache_folder: '.' found as path. \
            If you do not run './mcache test', look at the code.")
        path = os.path.dirname(os.path.realpath(__file__))

    root = os.path.abspath(os.sep)
    i = 0
    while path != root:
        mcache_path = os.path.join(path, folder)
        if os.path.isdir(mcache_path):
            return path
        path = os.path.split(path)[0]
        i += 1
        if i > 500:
            raise RuntimeError('recursion limit reached.')


    raise Exception("fatal: Not a mcache repository (or any parent up to %s').\
        \nRun mcache init [path]" % root)


def _init_(argv):
    """create a .mcache folder at pwd or given input"""
    if len(argv) > 1:  # path was given via stdin
        path = argv[1]
        makedir(path, ask=True)
    else:  # use current path
        path = os.curdir
        if path == '.':
            path = os.getcwd()

    path = os.path.join(path, '.mcache')
    makedir(path)


def info():
    print('No info yet.')


def parse_cmdline(argv):
    """parse cmdline input"""
    if argv[0] == 'init':
        _init_(argv)
    elif argv[0] == 'test':
        test()
    elif argv[0] == '--info':
        info()
    else:
        print("mcache: '%s' is not an mcache command." % argv[0])


def makedir(path, ask=False):
    """createse a directory if it does not exist"""
    if ask and not os.path.isdir(path):  # ask for permission
        ans = raw_input("directory '%s' does not exist.\nDo you want to create\
            it? [N/y]: " % path)
        if not ans.lower() == 'y':
            raise Exception("directory '%s' not created" % path)

    try:  # avoid race condition
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def test():

    @cache()
    def test_function(x):
        return x

    print(test_function(5))
    print(test_function(6))
    print(test_function(5))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        parse_cmdline(sys.argv[1:])
    else:
        info()
