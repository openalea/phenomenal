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


from alinea.phenomenal.plant_1 import (plant_1_images,
                                       plant_1_mask_adaptive_threshold)

from alinea.phenomenal.binarization_routine import line_adaptive_threshold
# ==============================================================================


def test_wrong_parameters_1():

    image = None
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        line_adaptive_threshold(image, mask)
    except Exception, e:
        assert e.message == 'image should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_2():

    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        line_adaptive_threshold(image, mask)
    except Exception, e:
        assert e.message == 'image should be 3D array'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_3():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mask = 42

    try:
        line_adaptive_threshold(image, mask)
    except Exception, e:
        assert e.message == 'mask should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        print False


def test_wrong_parameters_4():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        line_adaptive_threshold(image, mask)
    except Exception, e:
        assert e.message == 'image should be 2D array'
        assert type(e) == ValueError
    else:
        print False


def test_wrong_parameters_5():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mask = numpy.zeros((50, 50), dtype=numpy.uint8)

    try:
        line_adaptive_threshold(image, mask)
    except Exception, e:
        assert e.message == 'image and mask should have the same shape'
        assert type(e) == ValueError
    else:
        print False


def test_simply_working_1():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    binarize_image = line_adaptive_threshold(image, mask)

    assert (binarize_image == 0).all()
    assert binarize_image.ndim == 2
    assert binarize_image.shape == (25, 25)


def test_no_regression_1():

    images = plant_1_images()
    images.pop(-1)

    mask = plant_1_mask_adaptive_threshold()

    refs = [(0, 125245),
            (30, 107389),
            (60, 150358),
            (90, 135745),
            (120, 123639),
            (150, 128801),
            (180, 122822),
            (210, 84861),
            (240, 144506),
            (270, 128615),
            (300, 116146),
            (330, 121870)]

    for angle, ref in refs:

        img_bin = line_adaptive_threshold(
            images[angle], mask)

        assert numpy.count_nonzero(img_bin) == ref

# ==============================================================================

if __name__ == "__main__":

    test_wrong_parameters_1()
    test_wrong_parameters_2()
    test_wrong_parameters_3()
    test_wrong_parameters_4()
    test_wrong_parameters_5()

    test_simply_working_1()

    test_no_regression_1()
