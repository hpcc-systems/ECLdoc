import os

########################################################################

def split(arg, sep, apply=lambda x : x) :
    return [apply(x.strip()) for x in arg.split(sep) if len(x) != 0]

########################################################################

from jinja2 import contextfilter

@contextfilter
def call_macro_by_name(context, macro_name, *args, **kwargs):
    return context.vars[macro_name](*args, **kwargs)

########################################################################

def genPathTree(ecl_files, ext='') :
    '''
    Convert filepaths recovered from glob pattern into a tree structure
    '''
    path_tree = { "root" : {} }
    for file in ecl_files :
        path = os.path.normpath(file).split(os.sep)
        parent = path_tree["root"]
        for node in path[:-1] :
            if node not in parent :
                parent[node] = {}
            parent = parent[node]

        if path[-1].lower() == 'bundle.ecl' :
            path[-1] = 'bundle.ecl'
        parent[path[-1]] = file + ext

    return path_tree

def getRoot(path_tree, ecl_file) :
    '''
    walk the filepath tree to get parent of ecl_file
    '''
    path = os.path.normpath(ecl_file).split(os.sep)[:-1]
    parent_path = ''
    parent = path_tree['root']
    for node in path :
        parent = parent[node]
        parent_path = os.path.join(parent_path, node)

    return parent

########################################################################

def write_to_file(filename, text) :
    fp = open(filename, 'w')
    fp.write(text)
    fp.close()

def read_file(filename) :
    # Note the newline = ''.  This is required in order to prevent
    # <cr><nl> from being changed to <nl> which confuses the offsets.
    # The default, newline = None, casuses replacement.  Errors = 'replace'
    # causes bad UTF-8 chars to be replaced with '?'.
    return open(filename,'r', errors='strict', newline='').read()

########################################################################

def relpath(p1, p2) :
    return os.path.relpath(p1, p2)

def joinpath(*p1) :
    return os.path.join(*p1)

def dirname(p1) :
    return os.path.dirname(p1)

def realpath(p1) :
    return os.path.realpath(p1)
