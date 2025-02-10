# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
from __future__ import division, print_function

import skimage.morphology
import numpy
# ==============================================================================


def skeletonize_thinning(image):
    """
    Thinning is used to reduce each connected component in a binary image to a
    single-pixel wide skeleton

    :param image: binary image with 0 or 255
    :return: skeleton of a binary image.
    """
    img = image.copy().astype(numpy.uint8)

    img[img == 255] = 1
    skeleton = skimage.morphology.skeletonize(img)
    skeleton = skeleton.astype(numpy.uint8)
    skeleton[skeleton > 0] = 255

    return skeleton


def skeletonize_erode_dilate(image):
    """
    Erode and dilate image to build skeleton

    :param image: binary image with 0 or 255
    :return: skeleton of a binary image.
    """
    img = image.copy().astype(numpy.uint8)

    skeleton = numpy.zeros(img.shape, numpy.uint8)
    element = numpy.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])

    while numpy.count_nonzero(img) > 0:
        eroded = skimage.morphology.erosion(img, element)
        temp = skimage.morphology.dilation(eroded, element)
        temp = numpy.subtract(img, temp)
        skeleton = numpy.bitwise_or(skeleton, temp)
        img = eroded.copy()

    return skeleton
