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


import cv2
import numpy

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
    """
    Binarize a side view image of the PhenoArch platform, combining an HSV
    threshold and a mean shift threshold (difference with a mean image).

    Parameters
    ----------
    image : numpy.ndarray
        RGB image (uint8, 3-D array), as returned by `read_image` and the
        `data` module. Convert images read with OpenCV (BGR) first.
    mean_image : numpy.ndarray
        Mean image of the same shape, see `mean_image`.
    threshold : float, optional
        Threshold of the mean shift, see `threshold_meanshift`.
    dark_background : bool, optional
        Whether the plant is lighter than the background.
    hsv_min, hsv_max : tuple of int, optional
        Bounds of the HSV threshold, in OpenCV units (hue in [0, 180],
        saturation and value in [0, 255]).
    mask_mean_shift, mask_hsv : numpy.ndarray, optional
        2-D masks of the regions where each threshold applies.

    Returns
    -------
    numpy.ndarray
        Binary image (0 or 255).
    """
    # OpenCV HSV (hue in [0, 180], the units of hsv_min and hsv_max) of the RGB
    # image; PIL would give a hue in [0, 255]
    hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    binary_hsv_image = threshold_hsv(hsv_image, hsv_min, hsv_max, mask_hsv)

    binary_mean_shift_image = threshold_meanshift(
        image, mean_image, threshold, dark_background, mask_mean_shift
    )

    # saturated uint8 addition (cv2): numpy would give 254 where both are 255
    result = cv2.add(binary_hsv_image, binary_mean_shift_image)
    result = cv2.medianBlur(result, 3)

    return result
