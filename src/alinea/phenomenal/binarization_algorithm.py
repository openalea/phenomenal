# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s):
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import numpy
import cv2
# ==============================================================================


def mean_shift_binarization(image,
                            mean_image,
                            threshold=0.3,
                            dark_background=False,
                            mask=None):
    """

    Threshold pixels in image such as :
        image / mean_image <= (1 - threshhold).

    If dark_background is True (Inequality is reversed) :
        image / mean_image <= (1 + threshhold)

    Parameters
    ----------

    image : numpy.ndarray

    mean_image : numpy.ndarray

    threshold : float

    dark_background : bool

    mask = numpy.ndarray

    Returns
    -------
    out : numpy.ndarray

    """
    # ==========================================================================
    # Check Parameters
    if not isinstance(image, numpy.ndarray):
        raise TypeError('image should be a numpy.ndarray')
    if not isinstance(mean_image, numpy.ndarray):
        raise TypeError('mean_image should be a numpy.ndarray')
    if not isinstance(threshold, float):
        raise TypeError('threshold should be a float')
    if not isinstance(dark_background, bool):
        print dark_background
        raise TypeError('dark_background should be a bool')

    if image.ndim != 3:
        raise ValueError('image should be 3D array')
    if mean_image.ndim != 3:
        raise ValueError('mean_image should be 3D array')
    if image.shape != mean_image.shape:
        raise ValueError('image and mean_image should have the same shape')
    if not (0.0 <= threshold <= 1.0):
        raise ValueError('threshold should between 0.0 and 1.0=')

    if mask is not None:
        if not isinstance(mask, numpy.ndarray):
            raise TypeError('mask should be a numpy.ndarray')
        if mask.ndim != 2:
            raise ValueError('image should be 2D array')
        if image.shape[0:2] != mask.shape:
            raise ValueError('image and mask should have the same shape')
    # ==========================================================================

    image_f32 = numpy.float32(image)
    mean_image_f32 = numpy.float32(mean_image)

    with numpy.errstate(divide='ignore'):
        d = image_f32 / mean_image_f32

    if dark_background:
        if len(d.shape) > 2:  # color image
            d = d.max(2)
        dd = d >= (1. + threshold)
    else:
        if len(d.shape) > 2:  # color image
            d = d.min(2)
        dd = d <= (1. - threshold)

    dd = numpy.uint8(dd)

    if mask is not None:
        dd = cv2.bitwise_and(dd, mask)

    return dd


def hsv_binarization(image,
                     hsv_min,
                     hsv_max,
                     mask=None):
    """
    Binarize image with hsv_min and hsv_max parameters.
    => cv2.inRange(hsv_image, hsv_min, hsv_max)

    If mask is not None :
    => cv2.bitwise_and(binary_hsv_image, mask)
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

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    binary_hsv_image = cv2.inRange(hsv_image, hsv_min, hsv_max)

    if mask is not None:
        binary_hsv_image = cv2.bitwise_and(binary_hsv_image, mask)

    return binary_hsv_image


def get_mean_image(images):
    """
    Compute the mean image of a image list.

    :param images: A list of image.
    :return: A image who is the mean of the list image
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
