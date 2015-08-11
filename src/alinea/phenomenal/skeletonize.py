# -*- python -*-
#
#       test_reconstruction_3D_with_manual_calibration: Module Description
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
#       =======================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import
import cv2
import scipy
import numpy as np
import skimage.morphology

# =======================================================================
#       Local Import 

#       =======================================================================
#       Code


def skeletonize_image_skimage(image):
    """

    :param image:
    :return:
    """

    image[image == 255] = 1
    skeleton = skimage.morphology.skeletonize(image)
    skeleton = skeleton.astype(np.uint8)
    skeleton[skeleton > 0] = 255

    return skeleton


def skeletonize_image_opencv(image):
    skeleton = np.zeros(image.shape, np.uint8)

    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    while cv2.countNonZero(image) > 0:
        eroded = cv2.erode(image, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(image, temp)
        skeleton = cv2.bitwise_or(skeleton, temp)
        image = eroded.copy()

    return skeleton


