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

from alinea.phenomenal.segmentation_3d.peak_detection_algorithm import (
    peakdetect)
# ==============================================================================


def peak_detection(values, lookahead):
    lookahead = max(1, int(lookahead))

    max_peaks, min_peaks = peakdetect(
        values, range(len(values)), lookahead=lookahead)

    return max_peaks, min_peaks


def peak_detection_with_scipy(values, lookahead):
    lookahead = max(1, int(lookahead))

    max_peaks = scipy.signal.argrelmax(numpy.array(values), order=lookahead)[0]
    min_peaks = scipy.signal.argrelmin(numpy.array(values), order=lookahead)[0]

    return max_peaks, min_peaks
