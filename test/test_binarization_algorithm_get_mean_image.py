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

from alinea.phenomenal.binarization_algorithm import get_mean_image
# ==============================================================================


def test_wrong_parameters_1():
    try:
        get_mean_image(None)
    except Exception, e:
        assert e.message == 'images is not a list'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_2():
    try:
        get_mean_image(list())
    except Exception, e:
        assert e.message == 'images is empty'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_3():
    try:
        get_mean_image([[]])
    except Exception, e:
        assert e.message == 'image in list images is not a ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_4():
    try:
        get_mean_image([[]])
    except Exception, e:
        assert e.message == 'image in list images is not a ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_5():
    try:
        image = numpy.zeros((25, 25, 3))
        get_mean_image(image)
    except Exception, e:
        assert e.message == 'images is not a list'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_6():
    try:
        image = numpy.zeros((25, 25, 3))
        get_mean_image(image)
    except Exception, e:
        assert e.message == 'images is not a list'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_7():
    images = list()
    images.append(numpy.ones((25, 25, 3)))
    images.append(numpy.zeros((15, 15, 3)))

    try:
        get_mean_image(images)
    except Exception, e:
        assert e.message == 'Shape of ndarray image in list is different'
        assert type(e) == ValueError
    else:
        assert False


def test_simply_working_1():
    images = list()
    for i in range(10):
        images.append(numpy.zeros((25, 25, 3)))

    image = get_mean_image(images)
    assert numpy.count_nonzero(image) == 0
    assert image.ndim == 3
    assert image.shape == (25, 25, 3)


def test_simply_working_2():
    images = list()
    for i in range(10):
        images.append(numpy.ones((25, 25, 3)))

    image = get_mean_image(images)

    assert image.ndim == 3
    assert image.shape == (25, 25, 3)
    assert numpy.count_nonzero(image) == 25 * 25 * 3


def test_simply_working_3():
    images = list()
    for i in range(0, 1):
        images.append(numpy.ones((25, 25, 3)))
    for i in range(1, 10):
        images.append(numpy.zeros((25, 25, 3)))

    image = get_mean_image(images)
    assert (image == 0.1).all()
    assert image.ndim == 3
    assert image.shape == (25, 25, 3)


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
    test_simply_working_2()
    test_simply_working_3()
