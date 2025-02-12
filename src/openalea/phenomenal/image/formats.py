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

import numpy
from PIL import Image
# ==============================================================================


def read_image(filename, flag=None):
    """
    Read an image from a file name with opencv API.

    Parameters
    ----------
    filename: str
        file name of the image
    flag: str
        The PIL flag to convert the image
    Return
    ------
    img: numpy.ndarray
        RGB or grayscale image
    """

    img = Image.open(filename)
    if flag is not None:
        img = numpy.asarray(img.convert(flag), dtype=numpy.uint8)

    return img


def write_image(filename, image):
    """
    Write an image in a file.

    Parameters
    ----------
    filename: str
        output filename where write the image.
    image: numpy.ndarray
        numpy image to write.

    Returns
    -------
    None
    """
    if os.path.dirname(filename) and not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    Image.fromarray(image.astype(numpy.uint8)).save(filename)
