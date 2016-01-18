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
from alinea.phenomenal.binarization import (side_binarization_elcom,
                                            side_binarization_routine_elcom)
from alinea.phenomenal.binarization_algorithm import get_mean_image
from alinea.phenomenal.configuration import binarization_factor
# ==============================================================================


def test_wrong_parameters_1():

    factor = binarization_factor('factor_image_basic.cfg')
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        side_binarization_elcom(None, mean_image, factor)
    except Exception, e:
        assert e.message == 'image should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_2():

    factor = binarization_factor('factor_image_basic.cfg')
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        side_binarization_elcom(image, None, factor)
    except Exception, e:
        assert e.message == 'mean_image should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_3():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        side_binarization_elcom(image, mean_image, None)
    except Exception, e:
        assert e.message == 'factor should be a BinarizationFactor object'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_4():

    factor = binarization_factor('factor_image_basic.cfg')
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        side_binarization_elcom(image, mean_image, factor)
    except Exception, e:
        assert e.message == 'image should be 3D array'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_5():

    factor = binarization_factor('factor_image_basic.cfg')
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        side_binarization_elcom(image, mean_image, factor)
    except Exception, e:
        assert e.message == 'image should be 3D array'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_6():

    factor = binarization_factor('factor_image_basic.cfg')
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        side_binarization_elcom(image, mean_image, factor)
    except Exception, e:
        assert e.message == 'mean_image should be 3D array'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_7():
    factor = binarization_factor('factor_image_basic.cfg')
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.zeros((10, 10, 3), dtype=numpy.uint8)

    try:
        side_binarization_elcom(image, mean_image, factor)
    except Exception, e:
        assert e.message == 'image and mean_image should have the same shape'
        assert type(e) == ValueError
    else:
        assert False


def test_simply_working_1():
    factor = binarization_factor('factor_cubicle_6_elcom.cfg')

    img_1 = numpy.ones((2448, 2048, 3), dtype=numpy.uint8)
    img_2 = numpy.ones((2448, 2048, 3), dtype=numpy.uint8)
    mean_image = get_mean_image([img_1, img_2])

    img_binarize_1 = side_binarization_elcom(img_1, mean_image, factor)

    assert (img_binarize_1 == 0).all()
    assert img_binarize_1.ndim == 2
    assert img_binarize_1.shape == (2448, 2048)


def test_no_regression_1():

    factor = binarization_factor('factor_cubicle_6_elcom.cfg')

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

        image_0_binarize = side_binarization_elcom(
            img, mean_image, factor)

        assert numpy.count_nonzero(image_0_binarize) == ref

def test_no_regression_2():

    factor = binarization_factor('factor_cubicle_6_elcom.cfg')

    mask_mean_shift = factor.side_roi_main.mask
    mask_hsv = factor.side_roi_stem.mask

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

        image_0_binarize = side_binarization_routine_elcom(
            img,
            mean_image,
            hsv_min=(30, 25, 0),
            hsv_max=(150, 254, 165),
            mask_mean_shift=mask_mean_shift,
            mask_hsv=mask_hsv)

        assert numpy.count_nonzero(image_0_binarize) == ref


# ==============================================================================

if __name__ == "__main__":
    test_wrong_parameters_1()
    test_wrong_parameters_2()
    test_wrong_parameters_3()
    test_wrong_parameters_4()
    test_wrong_parameters_5()
    test_wrong_parameters_6()
    test_wrong_parameters_7()

    test_simply_working_1()

    test_no_regression_1()
    test_no_regression_2()
