# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
from __future__ import division, print_function

import numpy

import openalea.phenomenal.image as phm_img
# ==============================================================================


def test_mean_image_wrong_parameters_1():
    try:
        phm_img.mean_image(None)
    except Exception, e:
        assert type(e) == TypeError
    else:
        assert False


def test_mean_image_wrong_parameters_2():
    try:
        phm_img.mean_image(list())
    except Exception, e:
        assert type(e) == ValueError
    else:
        assert False


def test_mean_image_wrong_parameters_3():
    try:
        phm_img.mean_image([[]])
    except Exception, e:
        assert type(e) == TypeError
    else:
        assert False


def test_mean_image_wrong_parameters_4():
    try:
        phm_img.mean_image([[]])
    except Exception, e:
        assert type(e) == TypeError
    else:
        assert False


def test_mean_image_wrong_parameters_5():
    try:
        image = numpy.zeros((25, 25, 3))
        phm_img.mean_image(image)
    except Exception, e:
        assert type(e) == TypeError
    else:
        assert False


def test_mean_image_wrong_parameters_6():
    try:
        image = numpy.zeros((25, 25, 3))
        phm_img.mean_image(image)
    except Exception, e:
        assert type(e) == TypeError
    else:
        assert False


def test_mean_image_wrong_parameters_7():
    images = list()
    images.append(numpy.ones((25, 25, 3)))
    images.append(numpy.zeros((15, 15, 3)))

    try:
        phm_img.mean_image(images)
    except Exception, e:
        assert type(e) == ValueError
    else:
        assert False


def test_mean_image_1():
    images = list()
    for i in range(10):
        images.append(numpy.zeros((25, 25, 3)))

    image = phm_img.mean_image(images)
    assert numpy.count_nonzero(image) == 0
    assert image.ndim == 3
    assert image.shape == (25, 25, 3)


def test_mean_image_2():
    images = list()
    for i in range(10):
        images.append(numpy.ones((25, 25, 3)))

    image = phm_img.mean_image(images)

    assert image.ndim == 3
    assert image.shape == (25, 25, 3)
    assert numpy.count_nonzero(image) == 25 * 25 * 3


def test_mean_image_3():
    images = list()
    for i in range(0, 1):
        images.append(numpy.ones((25, 25, 3)))
    for i in range(1, 10):
        images.append(numpy.zeros((25, 25, 3)))

    image = phm_img.mean_image(images)
    assert (image == 0.1).all()
    assert image.ndim == 3
    assert image.shape == (25, 25, 3)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
