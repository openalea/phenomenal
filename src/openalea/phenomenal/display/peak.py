# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

from openalea.phenomenal.optional_deps import require_dependency



# ==============================================================================


def show_values(list_values, list_color):
    require_dependency('matplotlib', 'plot')
    import matplotlib.pyplot
    matplotlib.pyplot.figure()
    for values, color in zip(list_values, list_color):
        plot_values(values, color)
    matplotlib.pyplot.show()


def plot_values(values, color):
    require_dependency('matplotlib', 'plot')
    import matplotlib.pyplot
    matplotlib.pyplot.plot(range(len(values)), values, color)
