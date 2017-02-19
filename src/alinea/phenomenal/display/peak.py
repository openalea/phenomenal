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

from alinea.phenomenal.segmentation_3d.algorithm import smooth, peak_detection
# ==============================================================================


def show_values(list_values, list_color,
                normalize_values=True,
                smooth_values=True,
                plot_peak=True):

    matplotlib.pyplot.figure()
    for values, color in zip(list_values, list_color):
        plot_values(values, color,
                    normalize_values=normalize_values,
                    smooth_values=smooth_values,
                    plot_peak=plot_peak)
    matplotlib.pyplot.show()


def plot_values(values, color,
                normalize_values=True,
                smooth_values=True,
                plot_peak=True):
    if normalize_values:
        values = [v / float(sum(values)) for v in values]

    if smooth_values:
        values = smooth(numpy.array(values))

    matplotlib.pyplot.plot(range(len(values)), values, color)
    if plot_peak:
        max_peaks, min_peaks = peak_detection(values, 1)
        min_peaks = [(0, values[0])] + min_peaks
        for index, value in min_peaks:
            matplotlib.pyplot.plot(index, value, color + 'o')
