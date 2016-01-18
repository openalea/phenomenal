# -*- python -*-
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
# ==============================================================================
import numpy

from alinea.phenomenal.plant_1 import plant_1_images
from alinea.phenomenal.binarization import top_binarization_routine_hsv
# ==============================================================================


def test_top_binarization_hsv_1():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)

    binarize_image = top_binarization_routine_hsv(image, hsv_min, hsv_max)

    assert (binarize_image == 0).all()
    assert binarize_image.ndim == 2
    assert binarize_image.shape == (25, 25)


def test_no_regression_1():
    images = plant_1_images()
    image_top = images[-1]

    ref = 378897

    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)

    img_bin = top_binarization_routine_hsv(image_top, hsv_min, hsv_max)

    assert numpy.count_nonzero(img_bin) == ref

# ==============================================================================

if __name__ == "__main__":

    test_top_binarization_hsv_1()

    test_no_regression_1()
