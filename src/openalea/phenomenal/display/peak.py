# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import matplotlib.pyplot
import numpy

# ==============================================================================


def show_values(list_values, list_color,
                plot_peak=True):

    matplotlib.pyplot.figure()
    for values, color in zip(list_values, list_color):
        plot_values(values, color,
                    plot_peak=plot_peak)
    matplotlib.pyplot.show()


def plot_values(values, color,
                plot_peak=False):

    matplotlib.pyplot.plot(range(len(values)), values, color)


