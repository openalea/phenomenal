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
import openalea.opencv.extension as ocv2
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

    image_modify = ocv2.erode(image_modify, iterations=3)
    image_modify = ocv2.dilate(image_modify, iterations=3)

    if mask is not None:
        res = cv2.subtract(image, mask)
    else:
        res = image

    res = cv2.add(res, image_modify)

    res = ocv2.erode(res)
    res = ocv2.dilate(res)

    return res


def fill_up_prop(image):
    configuration_directory = shared_data(alinea.phenomenal)
    mask = cv2.imread(configuration_directory + "/roi_stem.png",
                      cv2.IMREAD_GRAYSCALE)

    if mask is not None:
        img = cv2.bitwise_and(image, image, mask=mask)

    kernel = np.ones((7, 7), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    img = cv2.add(image, img)

    return img
