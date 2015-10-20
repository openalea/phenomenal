# -*- python -*-
#
#       repair_processing.py :
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
import numpy as np

#       ========================================================================
#       Local Import
from openalea.deploy.shared_data import shared_data
import alinea.phenomenal


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


def fill_up_prop(image, is_top_image=False):

    img = image.copy()

    if is_top_image is False:
        configuration_directory = shared_data(alinea.phenomenal)
        mask = cv2.imread(configuration_directory + "/roi_stem.png",
                          cv2.IMREAD_GRAYSCALE)

        if mask is not None:
            img = cv2.bitwise_and(image, image, mask=mask)

    kernel = np.ones((7, 7), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    img = cv2.add(image, img)

    return img


def repair_processing(images):
    repair_images = dict()
    for angle in images:
        if angle == -1:
            repair_images[angle] = fill_up_prop(images[angle],
                                                is_top_image=True)
        else:
            repair_images[angle] = fill_up_prop(images[angle])

    return repair_images