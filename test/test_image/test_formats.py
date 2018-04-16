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

import os
import cv2
import numpy

import openalea.phenomenal.image as phm_img
# ==============================================================================


def test_1():

    im1 = numpy.zeros((400, 400))
    im1[10:-10, 10:-10] = 255

    phm_img.write_image("tmp.png", im1)
    im2 = phm_img.read_image("tmp.png", cv2.IMREAD_GRAYSCALE)

    assert numpy.array_equal(im1, im2)

    # delete the tmp file
    os.remove("tmp.png")


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
