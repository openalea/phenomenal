# -*- python -*-
#
#       skeletonize_2d.py : Function for skeletonize binary image
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
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
import skimage.morphology
import numpy as np

#       ========================================================================
#       Code


def skeletonize_thinning(image):
    """
    Thinning is used to reduce each connected component in a binary image to a
    single-pixel wide skeleton

    :param image: binary image with 0 or 255
    :return: skeleton of a binary image.
    """

    image[image == 255] = 1
    skeleton = skimage.morphology.skeletonize(image)
    skeleton = skeleton.astype(np.uint8)
    skeleton[skeleton > 0] = 255

    return skeleton


def skeletonize_erode_dilate(image):
    """
    Erode and dilate image to build skeleton

    :param image: binary image with 0 or 255
    :return: skeleton of a binary image.
    """


    skeleton = np.zeros(image.shape, np.uint8)

    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    while cv2.countNonZero(image) > 0:
        eroded = cv2.erode(image, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(image, temp)
        skeleton = cv2.bitwise_or(skeleton, temp)
        image = eroded.copy()

    return skeleton

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None






