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

from alinea.phenomenal.plant_1 import (plant_1_images,
                                       plant_1_mask_elcom_mean_shift,
                                       plant_1_mask_elcom_hsv)

from alinea.phenomenal.binarization_routine import meanshift_hsv_elcom
from alinea.phenomenal.binarization_algorithm import get_mean_image
# ==============================================================================


def test_simply_working_1():

    image = numpy.ones((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.ones((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (30, 11, 0)
    hsv_max = (129, 254, 141)
    mask_mean_shift = numpy.ones((25, 25), dtype=numpy.uint8)
    mask_hsv = numpy.ones((25, 25), dtype=numpy.uint8)

    img_bin = meanshift_hsv_elcom(
        image,
        mean_image,
        hsv_min=hsv_min,
        hsv_max=hsv_max,
        mask_mean_shift=mask_mean_shift,
        mask_hsv=mask_hsv)

    assert numpy.count_nonzero(img_bin) == 0
    assert img_bin.ndim == 2
    assert img_bin.shape == (25, 25)


def test_no_regression_1():

    mask_mean_shift = plant_1_mask_elcom_mean_shift()
    mask_hsv = plant_1_mask_elcom_hsv()

    images = plant_1_images()
    images.pop(-1)
    mean_image = get_mean_image(images.values())
    mean_image = mean_image[0:2448, 0:2048]

    refs = [(0, 130777),
            (30, 116158),
            (60, 157890),
            (90, 141508),
            (120, 131372),
            (150, 135760),
            (180, 129850),
            (210, 93736),
            (240, 154027),
            (270, 133624),
            (300, 121799),
            (330, 128745)]

    for angle, ref in refs:

        img = images[angle][0:2448, 0:2048, :]

        img_bin = meanshift_hsv_elcom(
            img,
            mean_image,
            hsv_min=(30, 25, 0),
            hsv_max=(150, 254, 165),
            mask_mean_shift=mask_mean_shift,
            mask_hsv=mask_hsv)

        assert numpy.count_nonzero(img_bin) == ref


# ==============================================================================

if __name__ == "__main__":
    test_simply_working_1()
    test_no_regression_1()
