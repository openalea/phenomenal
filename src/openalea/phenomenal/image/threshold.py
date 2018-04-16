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
Algorithms to threshold image
"""
# ==============================================================================
from __future__ import division, print_function

import cv2
import numpy
# ==============================================================================


def threshold_meanshift(image, mean_image,
                        threshold=0.3,
                        reverse=False,
                        mask=None):
    """
    Threshold pixels in numpy array such as::

        image / mean <= (1.0 - threshold)

    If reverse is True (Inequality is reversed)::

        image / mean <= (1.0 + threshold

    Parameters
    ----------
    image : numpy.ndarray of integers
        3-D array

    mean_image : numpy.ndarray of the same shape as 'image'
        3-D array 'mean_image'

    threshold : float, optional
        Threshold value. Must between 0.0 and 1.0

    reverse : bool, optional
       If True reverse inequality

    mask : numpy.ndarray, optional
        Array of same shape as `image`. Only points at which mask == True
        will be thresholded.

    Returns
    -------
    out : numpy.ndarray
        Thresholded binary image

    See Also
    --------
    get_mean_image, threshold_hsv

    """
    # ==========================================================================
    # Check Parameters
    if not isinstance(image, numpy.ndarray):
        raise TypeError('image should be a numpy.ndarray')
    if not isinstance(mean_image, numpy.ndarray):
        raise TypeError('mean should be a numpy.ndarray')
    if not isinstance(reverse, bool):
        raise TypeError('reverse should be a bool')

    if image.ndim != 3:
        raise ValueError('image should be 3D array')
    if mean_image.ndim != 3:
        raise ValueError('mean should be 3D array')
    if image.shape != mean_image.shape:
        raise ValueError('image and mean must have equal sizes')
    if not (0.0 <= threshold <= 1.0):
        raise ValueError('threshold must be between 0.0 and 1.0')

    if mask is not None:
        if not isinstance(mask, numpy.ndarray):
            raise TypeError('mask should be a numpy.ndarray')
        if mask.ndim != 2:
            raise ValueError('mask should be 2D array')
        if image.shape[0:2] != mask.shape:
            raise ValueError('mask and image must have equal sizes')
    # ==========================================================================

    with numpy.errstate(divide='ignore', invalid='ignore'):
        img = numpy.divide(numpy.float32(image), numpy.float32(mean_image))
        img[~ numpy.isfinite(img)] = 0

    if reverse:
        # Take max value of RGB tuple
        img = img.max(2)
        out = img >= (1. + threshold)
    else:
        # Take min value of RGB tuple
        img = img.min(2)
        out = img <= (1. - threshold)

    out = numpy.uint8(out)

    if mask is not None:
        out = cv2.bitwise_and(out, mask)

    del img

    return out * 255


def threshold_meanshift_enhance(image, mean_image,
                                threshold=0.3,
                                mask=None):
    # ==========================================================================

    image[image[:, :, 0] == 0] = 1
    image[image[:, :, 1] == 0] = 1
    image[image[:, :, 2] == 0] = 1

    mean_image[mean_image[:, :, 0] == 0] = 1
    mean_image[mean_image[:, :, 1] == 0] = 1
    mean_image[mean_image[:, :, 2] == 0] = 1

    img = numpy.divide(numpy.float32(image), numpy.float32(mean_image))

    # Take min value of RGB tuple
    out = img.min(2) <= (1. - threshold)
    out = numpy.uint8(out)

    if mask is not None:
        out = cv2.bitwise_and(out, mask)

    del img

    return out * 255


def threshold_hsv(image, hsv_min, hsv_max, mask=None):
    """
    Binarize HSV image with hsv_min and hsv_max parameters.
    => cv2.inRange(hsv_image, hsv_min, hsv_max)

    If mask is not None :
    => cv2.bitwise_and(binary_hsv_image, mask)

    Parameters
    ----------
    image : numpy.ndarray of integers
        3-D array of image RGB

    hsv_min : tuple of integers
        HSV value of minimum range

    hsv_max : tuple of integers
        HSV value of maximum range

    mask : numpy.ndarray, optional
        Array of same shape as `image`. Only points at which mask == True
        will be thresholded.

    Returns
    -------
    out : numpy.ndarray
        Thresholded binary image

    See Also
    --------
    threshold_meanshift
    """
    # ==========================================================================
    # Check Parameters
    if not isinstance(image, numpy.ndarray):
        raise TypeError('image should be a numpy.ndarray')
    if image.ndim != 3:
        raise ValueError('image should be 3D array')

    if not isinstance(hsv_min, tuple):
        raise TypeError('hsv_min should be a Tuple')
    if len(hsv_min) != 3:
        raise ValueError('hsv_min should be of size 3')
    for value in hsv_min:
        if not isinstance(value, int):
            raise ValueError('hsv_min value should be a integer')

    if not isinstance(hsv_max, tuple):
        raise TypeError('hsv_max should be a Tuple')
    if len(hsv_max) != 3:
        raise ValueError('hsv_max should be of size 3')
    for value in hsv_max:
        if not isinstance(value, int):
            raise ValueError('hsv_max value should be a integer')

    if mask is not None:
        if not isinstance(mask, numpy.ndarray):
            raise TypeError('mask should be a numpy.ndarray')
        if mask.ndim != 2:
            raise ValueError('mask should be 2D array')
        if image.shape[0:2] != mask.shape:
            raise ValueError('image and mask should have the same shape')
    # ==========================================================================

    out = cv2.inRange(image, hsv_min, hsv_max)

    if mask is not None:
        out = cv2.bitwise_and(out, mask)

    return out
