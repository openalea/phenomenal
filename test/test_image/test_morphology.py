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


def test_close_wrong_parameters_1():
    try:
        phm_img.close(None)
    except Exception as e:
        assert str(e) == "image must be a numpy.ndarray"
        assert isinstance(e, TypeError)
    else:
        assert False


def test_close_wrong_parameters_2():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        phm_img.close(image)
    except Exception as e:
        assert str(e) == "image must be 2D array"
        assert isinstance(e, ValueError)
    else:
        assert False


def test_close_wrong_parameters_3():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = 42
    try:
        phm_img.close(image, mask=mask)
    except Exception as e:
        assert str(e) == "mask must be a numpy.ndarray"
        assert isinstance(e, TypeError)
    else:
        assert False


def test_close_wrong_parameters_4():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        phm_img.close(image, mask=mask)
    except Exception as e:
        assert str(e) == "mask must be 2D array"
        assert isinstance(e, ValueError)
    else:
        assert False


def test_close_1():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    image_cleaning = phm_img.close(image, mask=mask)

    assert isinstance(image_cleaning, numpy.ndarray)
    assert image_cleaning.ndim == 2


def test_close_2():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)

    image_cleaning = phm_img.close(image)

    assert isinstance(image_cleaning, numpy.ndarray)
    assert image_cleaning.ndim == 2


# ==============================================================================
# MORPHOLOGY DILATE_ERODE TEST
# ==============================================================================


def test_dilate_erode_wrong_parameters_1():
    try:
        phm_img.dilate_erode(None)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_dilate_erode_wrong_parameters_2():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        phm_img.dilate_erode(image)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_dilate_erode_wrong_parameters_3():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = 42
    try:
        phm_img.dilate_erode(image, mask=mask)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_dilate_erode_wrong_parameters_4():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        phm_img.dilate_erode(image, mask=mask)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_dilate_erode_1():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    image_cleaning = phm_img.dilate_erode(image, mask=mask)

    assert isinstance(image_cleaning, numpy.ndarray)
    assert image_cleaning.ndim == 2


def test_dilate_erode_2():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)

    image_cleaning = phm_img.dilate_erode(image)

    assert isinstance(image_cleaning, numpy.ndarray)
    assert image_cleaning.ndim == 2


# ==============================================================================
# MORPHOLOGY ERODE_DILATE TEST
# ==============================================================================


def test_erode_dilate_wrong_parameters_1():
    try:
        phm_img.erode_dilate(None)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_erode_dilate_wrong_parameters_2():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        phm_img.erode_dilate(image)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_erode_dilate_wrong_parameters_3():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = 42
    try:
        phm_img.erode_dilate(image, mask=mask)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_erode_dilate_wrong_parameters_4():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        phm_img.erode_dilate(image, mask=mask)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_erode_dilate_1():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    image_cleaning = phm_img.erode_dilate(image, mask=mask)

    assert isinstance(image_cleaning, numpy.ndarray)
    assert image_cleaning.ndim == 2


def test_erode_dilate_2():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)

    image_cleaning = phm_img.erode_dilate(image)

    assert isinstance(image_cleaning, numpy.ndarray)
    assert image_cleaning.ndim == 2


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith("test_"):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
