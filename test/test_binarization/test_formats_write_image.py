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
import numpy
import os

from alinea.phenomenal.binarization.formats import write_image, read_image
# ==============================================================================


def test_simply_working_1():

    im1 = numpy.zeros((400, 400))
    im1[10:-10, 10:-10] = 255

    write_image(im1, "tmp.png")
    im2 = read_image("tmp.png")

    assert numpy.array_equal(im1, im2)

    # delete the tmp file
    os.remove("tmp.png")

if __name__ == "__main__":
    test_simply_working_1()
