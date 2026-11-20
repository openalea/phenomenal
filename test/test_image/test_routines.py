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


import numpy

import openalea.phenomenal.image as phm_img
# ==============================================================================


def test_mean_image_wrong_parameters_1():
    try:
        phm_img.mean_image(None)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_mean_image_wrong_parameters_2():
    try:
        phm_img.mean_image(list())
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_mean_image_wrong_parameters_3():
    try:
        phm_img.mean_image([[]])
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_mean_image_wrong_parameters_4():
    try:
        phm_img.mean_image([[]])
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_mean_image_wrong_parameters_5():
    try:
        image = numpy.zeros((25, 25, 3))
        phm_img.mean_image(image)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_mean_image_wrong_parameters_6():
    try:
        image = numpy.zeros((25, 25, 3))
        phm_img.mean_image(image)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_mean_image_wrong_parameters_7():
    images = [numpy.ones((25, 25, 3)), numpy.zeros((15, 15, 3))]

    try:
        phm_img.mean_image(images)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_mean_image_1():
    images =[]
    for i in range(10):
        images.append(numpy.zeros((25, 25, 3)))

    image = phm_img.mean_image(images)
    assert numpy.count_nonzero(image) == 0
    assert image.ndim == 3
    assert image.shape == (25, 25, 3)


def test_mean_image_2():
    images = []
    for i in range(10):
        images.append(numpy.ones((25, 25, 3)))

    image = phm_img.mean_image(images)

    assert image.ndim == 3
    assert image.shape == (25, 25, 3)
    assert numpy.count_nonzero(image) == 25 * 25 * 3


def test_mean_image_3():
    images = []
    for i in range(0, 1):
        images.append(numpy.ones((25, 25, 3)))
    for i in range(1, 10):
        images.append(numpy.zeros((25, 25, 3)))

    image = phm_img.mean_image(images)
    assert (image == 0.1).all()
    assert image.ndim == 3
    assert image.shape == (25, 25, 3)


def test_phenoarch_side_binarization_hsv_convention():
    # RGB image, hsv_min/hsv_max in OpenCV units (hue in [0, 180]); the default
    # hue range is [30, 150]. Blue (hue 120) is kept: read as BGR it would be
    # red, and with PIL its hue would be 170. Red (hue 0) is rejected.
    # The mean image equals the image, so the mean shift threshold selects nothing.
    for rgb, expected in (((10, 10, 120), 255), ((120, 10, 10), 0)):
        image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
        image[:, :] = rgb
        binary = phm_img.phenoarch_side_binarization(image, image.copy())
        assert binary.dtype == numpy.uint8
        assert (binary == expected).all(), rgb
