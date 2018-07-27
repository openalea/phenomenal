# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""
Post processing algorithms to improve binarization of a image
"""
# ==============================================================================
from __future__ import division, print_function

import cv2
import numpy
# ==============================================================================


def dilate_erode(binary_image,
                 kernel_shape=(3, 3),
                 iterations=1,
                 mask=None):
    """
    Applied a morphology (dilate & erode) on binary_image on a ROI.

    Parameters
    ----------
    binary_image : numpy.ndarray
        2-D array

    kernel_shape: (N, M) of integers, optional
        kernel shape of (dilate & erode) applied to binary_image

    iterations: int, optional
        number of successive iteration of (dilate & erode)

    mask : numpy.ndarray, optional
        Array of same shape as `image`. Only points at which mask == True
        will be processed.

    Returns
    -------
    out : numpy.ndarray
        Binary Image
    """
    # ==========================================================================
    # Check Parameters
    if not isinstance(binary_image, numpy.ndarray):
        raise TypeError('binary_image must be a numpy.ndarray')

    if binary_image.ndim != 2:
        raise ValueError('image must be 2D array')

    if mask is not None:
        if not isinstance(mask, numpy.ndarray):
            raise TypeError('mask must be a numpy.ndarray')
        if mask.ndim != 2:
            raise ValueError('mask must be 2D array')
    # ==========================================================================

    if mask is not None:
        out = cv2.bitwise_and(binary_image, mask)
    else:
        out = binary_image.copy()

    element = cv2.getStructuringElement(cv2.MORPH_CROSS, kernel_shape)
    out = cv2.dilate(out, element, iterations=iterations)
    out = cv2.erode(out, element, iterations=iterations)

    if mask is not None:
        res = cv2.subtract(binary_image, mask)
        out = cv2.add(res, out)

    return out


def erode_dilate(binary_image,
                 kernel_shape=(3, 3),
                 iterations=1,
                 mask=None):
    """
    Applied a morphology (erode & dilate) on binary_image on mask ROI.

    Parameters
    ----------
    binary_image : numpy.ndarray
        2-D array

    kernel_shape: (N, M) of integers, optional
        kernel shape of (erode & dilate) applied to binary_image

    iterations: int, optional
        number of successive iteration of (erode & dilate)

    mask : numpy.ndarray, optional
        Array of same shape as `image`. Only points at which mask == True
        will be processed.

    Returns
    -------
    out : numpy.ndarray
        Binary Image
    """
    # ==========================================================================
    # Check Parameters
    if not isinstance(binary_image, numpy.ndarray):
        raise TypeError('binary_image must be a numpy.ndarray')

    if binary_image.ndim != 2:
        raise ValueError('binary_image must be 2D array')

    if mask is not None:
        if not isinstance(mask, numpy.ndarray):
            raise TypeError('mask must be a numpy.ndarray')
        if mask.ndim != 2:
            raise ValueError('mask must be 2D array')
    # ==========================================================================

    if mask is not None:
        out = cv2.bitwise_and(binary_image, mask)
    else:
        out = binary_image.copy()

    element = cv2.getStructuringElement(cv2.MORPH_CROSS, kernel_shape)
    out = cv2.erode(out, element, iterations=iterations)
    out = cv2.dilate(out, element, iterations=iterations)

    if mask is not None:
        res = cv2.subtract(binary_image, mask)
        out = cv2.add(res, out)

    return out


def close(binary_image,
          kernel_shape=(7, 7),
          mask=None):
    """
    Applied a morphology close on binary_image on mask ROI.

    Parameters
    ----------
    binary_image : numpy.ndarray
        2-D array

    kernel_shape: (N, M) of integers
        kernel shape of morphology close applied to binary_image

    mask : numpy.ndarray, optional
        Array of same shape as `image`. Only points at which mask == True
        will be processed.

    Returns
    -------
    out : numpy.ndarray
        Binary Image
    """
    # ==========================================================================
    # Check Parameters
    if not isinstance(binary_image, numpy.ndarray):
        raise TypeError('image must be a numpy.ndarray')
    if binary_image.ndim != 2:
        raise ValueError('image must be 2D array')

    if mask is not None:
        if not isinstance(mask, numpy.ndarray):
            raise TypeError('mask must be a numpy.ndarray')
        if mask.ndim != 2:
            raise ValueError('mask must be 2D array')
    # ==========================================================================

    if mask is not None:
        out = cv2.bitwise_and(binary_image, mask)
    else:
        out = binary_image.copy()

    kernel = numpy.ones(kernel_shape, numpy.uint8)
    out = cv2.morphologyEx(out, cv2.MORPH_CLOSE, kernel)

    if mask is not None:
        out = cv2.add(binary_image, out)

    return out
