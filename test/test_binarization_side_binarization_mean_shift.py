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
import cv2


from alinea.phenomenal.plant_1 import (plant_1_images,
                                       plant_1_mask_mean_shift,
                                       plant_1_mask_hsv,
                                       plant_1_mask_clean_noise)

from alinea.phenomenal.binarization import (
    side_binarization_mean_shift,
    side_binarization_routine_mean_shift)
from alinea.phenomenal.binarization_algorithm import get_mean_image

from alinea.phenomenal.configuration import binarization_factor
# ==============================================================================


def test_wrong_parameters_1():

    factor = binarization_factor('factor_image_basic.cfg')
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        side_binarization_mean_shift(None, mean_image, factor)
    except Exception, e:
        assert e.message == 'image should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_2():

    factor = binarization_factor('factor_image_basic.cfg')
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        side_binarization_mean_shift(image, None, factor)
    except Exception, e:
        assert e.message == 'mean_image should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_3():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        side_binarization_mean_shift(image, mean_image, None)
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
        side_binarization_mean_shift(image, mean_image, factor)
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
        side_binarization_mean_shift(image, mean_image, factor)
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
        side_binarization_mean_shift(image, mean_image, factor)
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
        side_binarization_mean_shift(image, mean_image, factor)
    except Exception, e:
        assert e.message == 'image and mean_image should have the same shape'
        assert type(e) == ValueError
    else:
        assert False


def test_simply_working_1():
    factor = binarization_factor('factor_image_basic.cfg')

    img_1 = numpy.ones((2454, 2056, 3), dtype=numpy.uint8)
    img_2 = numpy.ones((2454, 2056, 3), dtype=numpy.uint8)
    mean_image = get_mean_image([img_1, img_2])

    img_binarize_1 = side_binarization_mean_shift(img_1, mean_image, factor)

    assert (img_binarize_1 == 0).all()
    assert img_binarize_1.ndim == 2
    assert img_binarize_1.shape == (2454, 2056)


def test_no_regression_1():

    factor = binarization_factor('factor_image_basic.cfg')

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

        img_bin = side_binarization_mean_shift(
            images[angle], mean_image, factor)

        assert numpy.count_nonzero(img_bin) == ref


def test_no_regression_2():

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
        img_bin = side_binarization_routine_mean_shift(
            images[angle],
            mean_image,
            hsv_min=(30, 11, 0),
            hsv_max=(129, 254, 141),
            mask_mean_shift=mask_mean_shift,
            mask_hsv=mask_hsv,
            mask_clean_noise=mask_clean_noise)

        assert numpy.count_nonzero(img_bin) == ref

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
