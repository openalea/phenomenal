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
from __future__ import division, print_function, absolute_import

import numpy
from PIL import Image
from skimage.filters import median

from .threshold import threshold_hsv, threshold_meanshift


# ==============================================================================


def mean_image(images):
    """
    Compute the mean of an image list.

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
        raise TypeError("images is not a list")
    if not images:
        raise ValueError("images is empty")

    shape_image_ref = None
    for image in images:
        if not isinstance(image, numpy.ndarray):
            raise TypeError("image in list images is not a ndarray")

        if shape_image_ref is None:
            shape_image_ref = numpy.shape(image)
        elif numpy.shape(image) != shape_image_ref:
            raise ValueError("Shape of ndarray image in list is different")
    # ==========================================================================

    length = len(images)
    weight = 1.0 / length
    h = images[0].shape[0]
    w = images[0].shape[1]

    mean = numpy.zeros((h, w, 3), float)
    for im in images:
        mean = mean + im * weight

    return mean


def phenoarch_side_binarization(
    image,
    mean_image,
    threshold=0.3,
    dark_background=False,
    hsv_min=(30, 25, 0),
    hsv_max=(150, 254, 165),
    mask_mean_shift=None,
    mask_hsv=None,
):
    hsv_image = numpy.asarray(Image.fromarray(image).convert("HSV"))
    binary_hsv_image = threshold_hsv(hsv_image, hsv_min, hsv_max, mask_hsv)

    binary_mean_shift_image = threshold_meanshift(
        image, mean_image, threshold, dark_background, mask_mean_shift
    )

    result = numpy.add(binary_hsv_image, binary_mean_shift_image)
    kernel = numpy.ones((3, 3), dtype=numpy.uint8)

    result = median(result, kernel)

    return result
