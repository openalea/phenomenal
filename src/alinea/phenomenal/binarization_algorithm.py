# -*- python -*-
#
#       binarization_algorithm: Module Description
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
#       =======================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import
import numpy
import cv2


#       =======================================================================
#       Local Import

#       =======================================================================

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

    :param image: Image of shape NxN
    :param mean_image: Image of shape NxN
    :param threshold: Float value
    :param dark_background: Boolean
    :param mask: Binary image
    :return: Binary Image
    """

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

    :param image: BGR image
    :param hsv_min:
    :param hsv_max:
    :param mask: Binary image
    :return: Binary image
    """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    binary_hsv_image = cv2.inRange(hsv_image, hsv_min, hsv_max)

    if mask is not None:
        binary_hsv_image = cv2.bitwise_and(binary_hsv_image, mask)

    return binary_hsv_image


def mixed_binarization(image,
                       mean_image,
                       hsv_min,
                       hsv_max,
                       threshold=0.3,
                       dark_background=False,
                       mask_meanshift=None,
                       mask_hsv=None):
    """

    :param image:
    :param mean_image:
    :param hsv_min:
    :param hsv_max:
    :param threshold:
    :param dark_background:
    :param mask_meanshift:
    :param mask_hsv:
    :return:
    """

    binary_hsv_image = hsv_binarization(image, hsv_min, hsv_max, mask_hsv)

    binary_meanshift_image = mean_shift_binarization(image,
                                                     mean_image,
                                                     threshold,
                                                     dark_background,
                                                     mask_meanshift)

    result = cv2.add(binary_hsv_image, binary_meanshift_image * 255)

    return result


def adaptive_thresh_gaussian_c(image,
                               block_size,
                               c,
                               mask=None):
    """

    :param image:
    :param block_size:
    :param c:
    :param mask:
    :return:
    """
    if mask is not None:
        image = cv2.bitwise_and(image, image, mask=mask)

    result = cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block_size,
        c)

    if mask is not None:
        result = cv2.bitwise_and(result, result, mask=mask)

    return result


def adaptive_thresh_mean_c(image,
                           block_size,
                           c,
                           mask=None):
    """

    :param image:
    :param block_size:
    :param c:
    :param mask:
    :return:
    """
    if mask is not None:
        image = cv2.bitwise_and(image, image, mask=mask)

    result = cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        block_size,
        c)

    if mask is not None:
        result = cv2.bitwise_and(result, result, mask=mask)

    return result
