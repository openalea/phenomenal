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
import cv2

from alinea.phenomenal.binarization_algorithm import threshold_hsv
# ==============================================================================


def test_wrong_parameters_1():

    image = None
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception, e:
        assert e.message == 'image should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_2():

    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception, e:
        assert e.message == 'image should be 3D array'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_3():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = None
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception, e:
        assert e.message == 'hsv_min should be a Tuple'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_4():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (80, 250, 1, 1)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception, e:
        assert e.message == 'hsv_min should be of size 3'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_5():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (80.6, 250.0, 56.9)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception, e:
        assert e.message == 'hsv_min value should be a integer'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_6():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = None
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception, e:
        assert e.message == 'hsv_max should be a Tuple'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_7():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception, e:
        assert e.message == 'hsv_max should be of size 3'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_8():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134.2)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception, e:
        assert e.message == 'hsv_max value should be a integer'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_9():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = 42

    try:
        threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception, e:
        assert e.message == 'mask should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_10():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception, e:
        assert e.message == 'mask should be 2D array'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_11():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 26), dtype=numpy.uint8)

    try:
        threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception, e:
        assert e.message == 'image and mask should have the same shape'
        assert type(e) == ValueError
    else:
        assert False


def test_simply_working_1():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    img_bin = threshold_hsv(image, hsv_min, hsv_max, mask=mask)

    assert img_bin.ndim == 2
    assert numpy.count_nonzero(img_bin) == 0

if __name__ == "__main__":
    test_wrong_parameters_1()
    test_wrong_parameters_2()
    test_wrong_parameters_3()
    test_wrong_parameters_4()
    test_wrong_parameters_5()
    test_wrong_parameters_6()
    test_wrong_parameters_7()
    test_wrong_parameters_8()
    test_wrong_parameters_9()
    test_wrong_parameters_10()
    test_wrong_parameters_11()

    test_simply_working_1()
