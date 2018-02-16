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
import numpy
import scipy.signal

# ==============================================================================


def peak_detection(values, order=3):

    order = max(1, int(order))
    max_peaks = scipy.signal.argrelextrema(numpy.array(values),
                                           numpy.greater_equal,
                                           order=order)[0]

    min_peaks = scipy.signal.argrelextrema(numpy.array(values),
                                           numpy.less_equal,
                                           order=order)[0]

    max_peaks = [(i, values[i]) for i in max_peaks]
    min_peaks = [(i, values[i]) for i in min_peaks]

    return max_peaks, min_peaks