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
                                       plant_1_mask_mean_shift,
                                       plant_1_mask_hsv,
                                       plant_1_mask_clean_noise)
from alinea.phenomenal.binarization_routine import meanshift_hsv
from alinea.phenomenal.binarization_algorithm import get_mean_image

# ==============================================================================


def test_simply_working_1():

    image = numpy.ones((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.ones((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (30, 11, 0)
    hsv_max = (129, 254, 141)
    mask_mean_shift = numpy.ones((25, 25), dtype=numpy.uint8)
    mask_hsv = numpy.ones((25, 25), dtype=numpy.uint8)
    mask_clean_noise = numpy.ones((25, 25), dtype=numpy.uint8)

    img_bin = meanshift_hsv(
        image,
        mean_image,
        hsv_min=hsv_min,
        hsv_max=hsv_max,
        mask_mean_shift=mask_mean_shift,
        mask_hsv=mask_hsv,
        mask_clean_noise=mask_clean_noise)

    assert (img_bin == 0).all()
    assert img_bin.ndim == 2
    assert img_bin.shape == (25, 25)


def test_no_regression_1():

    hsv_min = (30, 11, 0)
    hsv_max = (129, 254, 141)
    mask_mean_shift = plant_1_mask_mean_shift()
    mask_hsv = plant_1_mask_hsv()
    mask_clean_noise = plant_1_mask_clean_noise()

    images = plant_1_images()
    images.pop(-1)
    mean_image = get_mean_image(images.values())

    refs = [(0, 125523),
            (30, 107976),
            (60, 149982),
            (90, 136723),
            (120, 123908),
            (150, 127905),
            (180, 124630),
            (210, 85217),
            (240, 146001),
            (270, 128843),
            (300, 114866),
            (330, 121175)]

    for angle, ref in refs:
        img_bin = meanshift_hsv(
            images[angle],
            mean_image,
            hsv_min=hsv_min,
            hsv_max=hsv_max,
            mask_mean_shift=mask_mean_shift,
            mask_hsv=mask_hsv,
            mask_clean_noise=mask_clean_noise)

        assert numpy.count_nonzero(img_bin) == ref

# ==============================================================================

if __name__ == "__main__":
    test_simply_working_1()
    test_no_regression_1()
