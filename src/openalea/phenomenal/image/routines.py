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
"""
Routines functions to binarize images
"""
# ==============================================================================
from __future__ import division, print_function

import cv2
import numpy

from .threshold import threshold_hsv, threshold_meanshift
# ==============================================================================


def mean_image(images):
    """
    Compute the mean of a image list.

    Parameters
    ----------
    images : [ numpy.ndarray of integers ]
        list of 3-D array

    Returns
    -------
    out : numpy.ndarray
         Mean of the list image

    See Also
    --------
    threshold_meanshift
    """
    # ==========================================================================
    # Check Parameters
    if not isinstance(images, list):
        raise TypeError('images is not a list')
    if not images:
        raise ValueError('images is empty')

    shape_image_ref = None
    for image in images:
        if not isinstance(image, numpy.ndarray):
            raise TypeError('image in list images is not a ndarray')

        if shape_image_ref is None:
            shape_image_ref = numpy.shape(image)
        elif numpy.shape(image) != shape_image_ref:
            raise ValueError('Shape of ndarray image in list is different')
    # ==========================================================================

    length = len(images)
    weight = 1. / length

    start = cv2.addWeighted(images[0], weight, images[1], weight, 0)

    return reduce(lambda x, y: cv2.addWeighted(x, 1, y, weight, 0),
                  images[2:],
                  start)


def phenoarch_side_binarization(image,
                                mean_image,
                                threshold=0.3,
                                dark_background=False,
                                hsv_min=(30, 25, 0),
                                hsv_max=(150, 254, 165),
                                mask_mean_shift=None,
                                mask_hsv=None):

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    binary_hsv_image = threshold_hsv(hsv_image, hsv_min, hsv_max, mask_hsv)

    binary_mean_shift_image = threshold_meanshift(
        image, mean_image, threshold, dark_background, mask_mean_shift)

    result = cv2.add(binary_hsv_image, binary_mean_shift_image)

    result = cv2.medianBlur(result, 3)

    return result
