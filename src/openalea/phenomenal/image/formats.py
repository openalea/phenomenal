# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""
Formats module to read/write image
"""
# ==============================================================================
from __future__ import division, print_function

import os
import cv2
# ==============================================================================


def read_image(filename, flags=cv2.IMREAD_UNCHANGED):
    """
    Read a image from a file name with opencv API.

    :param filename: file name of the image
    :param flags:
    :return: RGB or grayscale image
    """
    img = cv2.imread(filename, flags=flags)

    shape = img.shape
    if len(shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img


def write_image(filename, image):
    """
    Write a image in a file.

    :param filename: output filename where write the image
    :param image: numpy image to write
    :return: None
    """
    if (os.path.dirname(filename) and not os.path.exists(
            os.path.dirname(filename))):
        os.makedirs(os.path.dirname(filename))

    cv2.imwrite(filename, image)
