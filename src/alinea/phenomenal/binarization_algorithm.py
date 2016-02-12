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
"""
Algorithms to threshold image
"""
# ==============================================================================
import numpy
import cv2
# ==============================================================================


def threshold_meanshift(image,
                        mean,
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

    mean : numpy.ndarray of the same shape as 'image'
        3-D array 'mean'

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
    if not isinstance(mean, numpy.ndarray):
        raise TypeError('mean should be a numpy.ndarray')
    if not isinstance(threshold, float):
        raise TypeError('threshold should be a float')
    if not isinstance(reverse, bool):
        raise TypeError('reverse should be a bool')

    if image.ndim != 3:
        raise ValueError('image should be 3D array')
    if mean.ndim != 3:
        raise ValueError('mean should be 3D array')
    if image.shape != mean.shape:
        raise ValueError('image and mean must have equal sizes')
    if not (0.0 <= threshold <= 1.0):
        raise ValueError('threshold must be between 0.0 and 1.0')

    if mask is not None:
        if not isinstance(mask, numpy.ndarray):
            raise TypeError('mask should be a numpy.ndarray')
        if mask.ndim != 2:
            raise ValueError('image should be 2D array')
        if image.shape[0:2] != mask.shape:
            raise ValueError('mask and image must have equal sizes')
    # ==========================================================================

    with numpy.errstate(divide='ignore'):
        img = numpy.divide(numpy.float32(image), numpy.float32(mean))

    if reverse:
        img = img.max(2)
        out = img >= (1. + threshold)
    else:
        img = img.min(2)
        out = img <= (1. - threshold)

    out = numpy.uint8(out)

    if mask is not None:
        out = cv2.bitwise_and(out, mask)

    return out


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


def get_mean_image(images):
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
    function = lambda x, y: cv2.addWeighted(x, 1, y, weight, 0)

    return reduce(function, images[2:], start)
