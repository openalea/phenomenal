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

from alinea.phenomenal.plant_1 import plant_1_images
from alinea.phenomenal.binarization_algorithm import (threshold_meanshift,
                                                      get_mean_image)
# ==============================================================================


def test_wrong_parameters_1():
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        threshold_meanshift(None, mean_image)
    except Exception, e:
        assert e.message == 'image should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_2():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        threshold_meanshift(image, None)
    except Exception, e:
        assert e.message == 'mean should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_3():

    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        threshold_meanshift(image, mean_image)
    except Exception, e:
        assert e.message == 'image should be 3D array'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_4():

    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        threshold_meanshift(image, mean_image)
    except Exception, e:
        assert e.message == 'image should be 3D array'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_5():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        threshold_meanshift(image, mean_image)
    except Exception, e:
        assert e.message == 'mean should be 3D array'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_6():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.zeros((10, 10, 3), dtype=numpy.uint8)

    try:
        threshold_meanshift(image, mean_image)
    except Exception, e:
        assert e.message == 'image and mean must have equal sizes'
        assert type(e) == ValueError
    else:
        assert False


def test_simply_working_1():
    images = list()
    images.append(numpy.zeros((25, 25, 3), numpy.uint8))
    images.append(numpy.zeros((25, 25, 3), numpy.uint8))
    mean_image = get_mean_image(images)

    assert mean_image.shape == (25, 25, 3)
    assert mean_image.ndim == 3
    assert numpy.count_nonzero(mean_image) == 0


def test_no_regression_1():
    images = plant_1_images()
    images.pop(-1)
    mean_image = get_mean_image(images.values())

    refs = [(0, 129070),
            (30, 116665),
            (60, 163168),
            (90, 144319),
            (120, 135900),
            (150, 140360),
            (180, 131963),
            (210, 92803),
            (240, 155876),
            (270, 134983),
            (300, 124941),
            (330, 131898)]

    for angle, ref in refs:
        image_0_binarize = threshold_meanshift(images[angle], mean_image)
        image_0_binarize *= 255
        assert numpy.count_nonzero(image_0_binarize) == ref

# ==============================================================================

if __name__ == "__main__":
    test_wrong_parameters_1()
    test_wrong_parameters_2()
    test_wrong_parameters_3()
    test_wrong_parameters_4()
    test_wrong_parameters_5()
    test_wrong_parameters_6()

    test_simply_working_1()

    test_no_regression_1()

