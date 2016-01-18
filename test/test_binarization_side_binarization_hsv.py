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
from alinea.phenomenal.binarization import (side_binarization_hsv,
                                            side_binarization_routine_hsv)
from alinea.phenomenal.configuration import binarization_factor
# ==============================================================================


def test_wrong_parameters_1():

    factor_side_binarization = binarization_factor('factor_image_basic.cfg')

    try:
        side_binarization_hsv(None, factor_side_binarization)
    except Exception, e:
        assert e.message == 'image should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_2():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        side_binarization_hsv(image, None)
    except Exception, e:
        assert e.message == 'factor should be a BinarizationFactor object'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_3():

    factor_side_binarization = binarization_factor('factor_image_basic.cfg')
    image = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        side_binarization_hsv(image, factor_side_binarization)
    except Exception, e:
        assert e.message == 'image should be 3D array'
        assert type(e) == ValueError
    else:
        print False


def test_side_binarization_hsv_1():

    factor = binarization_factor('factor_image_basic.cfg')
    image = numpy.zeros((2454, 2056, 3), dtype=numpy.uint8)

    binarize_image = side_binarization_hsv(image, factor)

    assert (binarize_image == 0).all()
    assert binarize_image.ndim == 2
    assert binarize_image.shape == (2454, 2056)


def test_no_regression_1():
    factor = binarization_factor('factor_image_basic.cfg')

    images = plant_1_images()
    images.pop(-1)

    refs = [(0, 121726),
            (30, 104465),
            (60, 141807),
            (90, 126528),
            (120, 114964),
            (150, 118759),
            (180, 118949),
            (210, 83357),
            (240, 139211),
            (270, 120737),
            (300, 108052),
            (330, 113243)]

    for angle, ref in refs:
        image_0_binarize = side_binarization_hsv(images[angle], factor)

        assert numpy.count_nonzero(image_0_binarize) == ref


def test_no_regression_2():
    factor = binarization_factor('factor_image_basic.cfg')

    cubicle_domain = factor.side_cubicle_domain
    cubicle_background = factor.side_cubicle_background
    main_hsv_min = factor.side_roi_main.hsv_min
    main_hsv_max = factor.side_roi_main.hsv_max
    main_mask = factor.side_roi_main.mask
    orange_band_mask = factor.side_roi_orange_band.mask
    pot_hsv_min = factor.side_roi_pot.hsv_min
    pot_hsv_max = factor.side_roi_pot.hsv_max
    pot_mask = factor.side_roi_pot.mask

    images = plant_1_images()
    images.pop(-1)

    refs = [(0, 121726),
            (30, 104465),
            (60, 141807),
            (90, 126528),
            (120, 114964),
            (150, 118759),
            (180, 118949),
            (210, 83357),
            (240, 139211),
            (270, 120737),
            (300, 108052),
            (330, 113243)]

    for angle, ref in refs:
        image_0_binarize = side_binarization_routine_hsv(
            images[angle],
            cubicle_domain,
            cubicle_background,
            main_hsv_min,
            main_hsv_max,
            main_mask,
            orange_band_mask,
            pot_hsv_min,
            pot_hsv_max,
            pot_mask)

        assert numpy.count_nonzero(image_0_binarize) == ref


# ==============================================================================

if __name__ == "__main__":
    test_wrong_parameters_1()
    test_wrong_parameters_2()
    test_wrong_parameters_3()

    test_side_binarization_hsv_1()

    test_no_regression_1()
    test_no_regression_2()
