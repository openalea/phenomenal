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

from alinea.phenomenal.binarization import (side_binarization_mean_shift,
                                            get_mean_image)
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


def test_side_binarization_mean_shift_1():
    factor = binarization_factor('factor_image_basic.cfg')

    img_1 = numpy.ones((2454, 2056, 3), dtype=numpy.uint8)
    img_2 = numpy.ones((2454, 2056, 3), dtype=numpy.uint8)
    mean_image = get_mean_image([img_1, img_2])

    img_binarize_1 = side_binarization_mean_shift(img_1, mean_image, factor)

    assert (img_binarize_1 == 0).all()
    assert img_binarize_1.ndim == 2
    assert img_binarize_1.shape == (2454, 2056)

# ==============================================================================

if __name__ == "__main__":
    test_wrong_parameters_1()
    test_wrong_parameters_2()
    test_wrong_parameters_3()
    test_wrong_parameters_4()
    test_wrong_parameters_5()
    test_wrong_parameters_6()
    test_wrong_parameters_7()

    test_side_binarization_mean_shift_1()
