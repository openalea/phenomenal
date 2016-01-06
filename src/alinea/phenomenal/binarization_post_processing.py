# -*- python -*-
#
#       binarization_post_processing.py :
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
#       ========================================================================

#       ========================================================================
#       External Import 
import cv2
import numpy

#       ========================================================================
#       Local Import

#       ========================================================================


def clean_noise(image, mask=None):
    """
    Goal: Cleaning orange band noise with mask

    Applied mask on image then erode and dilate on 3 iteration.
    Applied subtract image and mask and add to image modify before
    And finally, erode and dilate again

    :param image: Binary Image
    :param mask:
    :return: Binary image
    """
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


def remove_plant_support_from_image(image, is_top_image=False, mask=None):

    img = image.copy()

    if is_top_image is False and mask is not None:
        img = cv2.bitwise_and(image, image, mask=mask)

    kernel = numpy.ones((7, 7),numpy.uint8)

    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    img = cv2.add(image, img)

    return img


def remove_plant_support_from_images(images, mask=None):

    post_processing_images = dict()
    for angle in images:
        if angle < 0:
            post_processing_images[angle] = remove_plant_support_from_image(
                images[angle], is_top_image=True, mask=mask)
        else:
            post_processing_images[angle] = remove_plant_support_from_image(
                images[angle], is_top_image=False, mask=mask)

    return post_processing_images
