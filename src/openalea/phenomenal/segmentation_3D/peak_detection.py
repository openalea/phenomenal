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


def peak_detection(values, lookahead):
    lookahead = max(1, int(lookahead))

    max_peaks = scipy.signal.argrelmax(numpy.array(values), order=lookahead)[0]
    min_peaks = scipy.signal.argrelmin(numpy.array(values), order=lookahead)[0]

    max_peaks = [(i, values[i]) for i in max_peaks]
    min_peaks = [(i, values[i]) for i in min_peaks]

    return max_peaks, min_peaks
