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
import cv2
import numpy
# ==============================================================================


def clean_noise(image, mask=None):
    """
    Cleaning orange band noise with mask

    Applied mask on image then erode and dilate on 3 iteration.
    Applied subtract image and mask and add to image modify before
    And finally, erode and dilate again

    Parameters
    ----------

    image : numpy.array
    Binary Image

    mask : numpy.array

    Returns
    -------
    out : numpy.array
    Binary Image

    """
    # ==========================================================================
    # Check Parameters
    if not isinstance(image, numpy.ndarray):
        raise TypeError('image should be a numpy.ndarray')

    if image.ndim != 2:
        raise ValueError('image should be 2D array')

    if mask is not None:
        if not isinstance(mask, numpy.ndarray):
            raise TypeError('mask should be a numpy.ndarray')
        if mask.ndim != 2:
            raise ValueError('mask should be 2D array')
    # ==========================================================================

    if mask is not None:
        image_modify = cv2.bitwise_and(image, mask)
    else:
        image_modify = image

    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    image_modify = cv2.erode(image_modify, element, iterations=3)
    image_modify = cv2.dilate(image_modify, element, iterations=3)

    if mask is not None:
        res = cv2.subtract(image, mask)
    else:
        res = image

    res = cv2.add(res, image_modify)

    res = cv2.erode(res, element, iterations=1)
    res = cv2.dilate(res, element, iterations=1)

    return res


def remove_plant_support(image, mask=None):
    """
    remove_plant_support(numpy.array, mask=None)

        Remove plant support from image with mask.

        Parameters
        ----------

        image : numpy.array
            Binary Image

        mask : numpy.array

        Returns
        -------
        out : numpy.array
            Binary Image
    """
    # ==========================================================================
    # Check Parameters
    if not isinstance(image, numpy.ndarray):
        raise TypeError('image should be a numpy.ndarray')

    if image.ndim != 2:
        raise ValueError('image should be 2D array')

    if mask is not None:
        if not isinstance(mask, numpy.ndarray):
            raise TypeError('mask should be a numpy.ndarray')
        if mask.ndim != 2:
            raise ValueError('mask should be 2D array')
    # ==========================================================================
    img = image.copy()

    if mask is not None:
        img = cv2.bitwise_and(image, image, mask=mask)

    kernel = numpy.ones((7, 7), numpy.uint8)

    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    img = cv2.add(image, img)

    return img

