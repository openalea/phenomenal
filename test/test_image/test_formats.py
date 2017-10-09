# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import os
import numpy


from openalea.phenomenal.image import (
    read_image, write_image)

# ==============================================================================


def test_simply_working_1():

    file_name = os.path.dirname(__file__) + "/data/150.png"
    im = read_image(file_name)

    assert im.shape == (495, 415, 3)


def test_write_image():

    im1 = numpy.zeros((400, 400))
    im1[10:-10, 10:-10] = 255

    write_image("tmp.png", im1)
    im2 = read_image("tmp.png")

    assert numpy.array_equal(im1, im2)

    # delete the tmp file
    os.remove("tmp.png")


# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
