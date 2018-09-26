# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
from __future__ import division, print_function

import os.path
import glob
import subprocess
# ==============================================================================


def t_notebook(filename):

    command = ("jupyter nbconvert --to notebook --execute "
               "--ExecutePreprocessor.timeout=6000 \"{}\"".format(filename))

    try:
        with open(os.devnull, 'wb') as devnull:
            error = subprocess.call(command,
                                    shell=True,
                                    stdout=devnull,
                                    stderr=devnull)
    except:
        error = True

    return bool(error)


def clean(old_filenames, new_filenames):
    for filename in new_filenames:
        if filename not in old_filenames:
            os.remove(filename)


def t_directory(dirname):

    all_filenames = glob.glob(os.path.join(dirname, "*"))
    notebook_filenames = glob.glob(os.path.join(dirname, "*.ipynb"))

    for filename in notebook_filenames:
        error = t_notebook(filename)
        new_filenames = glob.glob(os.path.join(dirname, "*"))
        clean(all_filenames, new_filenames)
        print("{} - {}".format(filename, "ERROR" if error else "OK"))
        assert bool(error) is False


# def test_notebook():
#     try:
#         import ipyvolume
#         import nbconvert
#         import notebook
#         import jupyter
#     except ImportError:
#         return
#
#     dirname = os.path.dirname(__file__)
#     dirname_example = os.path.abspath(os.path.join(dirname, '../../examples/'))
#
#     t_directory(dirname_example)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
