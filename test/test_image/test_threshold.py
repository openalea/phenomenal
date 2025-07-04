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


from __future__ import absolute_import
import numpy

import openalea.phenomenal.image as phm_img
# ==============================================================================


def test_threshold_hsv_wrong_parameters_1():
    image = None
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_threshold_hsv_wrong_parameters_2():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_hsv_wrong_parameters_3():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = None
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_threshold_hsv_wrong_parameters_4():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (80, 250, 1, 1)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_hsv_wrong_parameters_5():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (80.6, 250.0, 56.9)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_hsv_wrong_parameters_6():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = None
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_threshold_hsv_wrong_parameters_7():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_hsv_wrong_parameters_8():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134.2)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_hsv_wrong_parameters_9():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = 42

    try:
        phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_threshold_hsv_wrong_parameters_10():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_hsv_wrong_parameters_13():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 26), dtype=numpy.uint8)

    try:
        phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_hsv_1():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    img_bin = phm_img.threshold_hsv(image, hsv_min, hsv_max, mask=mask)

    assert img_bin.ndim == 2
    assert numpy.count_nonzero(img_bin) == 0


# ==============================================================================


def test_threshold_meanshift_wrong_parameters_1():
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        phm_img.threshold_meanshift(None, mean_image)
    except Exception as e:
        assert str(e) == "image should be a numpy.ndarray"
        assert isinstance(e, TypeError)
    else:
        assert False


def test_threshold_meanshift_wrong_parameters_2():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        phm_img.threshold_meanshift(image, None)
    except Exception as e:
        assert str(e) == "mean should be a numpy.ndarray"
        assert isinstance(e, TypeError)
    else:
        assert False


def test_threshold_meanshift_wrong_parameters_3():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        phm_img.threshold_meanshift(image, mean_image)
    except Exception as e:
        assert str(e) == "image should be 3D array"
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_meanshift_wrong_parameters_4():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mean_im = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        phm_img.threshold_meanshift(image, mean_im)
    except Exception as e:
        assert str(e) == "image should be 3D array"
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_meanshift_wrong_parameters_5():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_im = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        phm_img.threshold_meanshift(image, mean_im)
    except Exception as e:
        assert str(e) == "mean should be 3D array"
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_meanshift_wrong_parameters_6():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_im = numpy.zeros((10, 10, 3), dtype=numpy.uint8)

    try:
        phm_img.threshold_meanshift(image, mean_im)
    except Exception as e:
        assert str(e) == "image and mean must have equal sizes"
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_meanshift_wrong_parameters_7():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_im = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        phm_img.threshold_meanshift(image, mean_im)
    except Exception as e:
        assert str(e) == "mean should be 3D array"
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_meanshift_wrong_parameters_8():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_im = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        phm_img.threshold_meanshift(image, mean_im, threshold=2)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_meanshift_wrong_parameters_9():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        phm_img.threshold_meanshift(image, mean_image, reverse=None)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_threshold_meanshift_wrong_parameters_10():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mask = [[1, 1, 1]]

    try:
        phm_img.threshold_meanshift(image, mean_image, mask=mask)
    except Exception as e:
        assert isinstance(e, TypeError)
    else:
        assert False


def test_threshold_meanshift_wrong_parameters_11():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        phm_img.threshold_meanshift(image, mean_image, mask=mask)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_meanshift_wrong_parameters_12():
    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mean_image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    mask = numpy.zeros((25, 26), dtype=numpy.uint8)

    try:
        phm_img.threshold_meanshift(image, mean_image, mask=mask)
    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_threshold_meanshift_1():
    im1 = numpy.zeros((25, 25, 3), numpy.uint8)
    im2 = numpy.zeros((25, 25, 3), numpy.uint8)

    mean_im = phm_img.mean_image(list([im1, im2]))

    bin_img = phm_img.threshold_meanshift(im1, mean_im)

    assert bin_img.shape == (25, 25)


def test_threshold_meanshift_2():
    im1 = numpy.zeros((25, 25, 3), numpy.uint8)
    im2 = numpy.zeros((25, 25, 3), numpy.uint8)
    mask = numpy.zeros((25, 25), numpy.uint8)

    mean_im = phm_img.mean_image(list([im1, im2]))

    bin_img = phm_img.threshold_meanshift(im1, mean_im, mask=mask)
    assert bin_img.shape == (25, 25)


def test_threshold_meanshift_3():
    im1 = numpy.zeros((25, 25, 3), numpy.uint8)
    im2 = numpy.zeros((25, 25, 3), numpy.uint8)
    mask = numpy.zeros((25, 25), numpy.uint8)

    mean_im = phm_img.mean_image(list([im1, im2]))

    bin_img = phm_img.threshold_meanshift(im1, mean_im, mask=mask, threshold=1)
    assert bin_img.shape == (25, 25)


def test_threshold_meanshift_4():
    im1 = numpy.zeros((25, 25, 3), numpy.uint8)
    im2 = numpy.zeros((25, 25, 3), numpy.uint8)
    mask = numpy.zeros((25, 25), numpy.uint8)

    mean_im = phm_img.mean_image(list([im1, im2]))

    bin_img = phm_img.threshold_meanshift(im1, mean_im, mask=mask, reverse=True)
    assert bin_img.shape == (25, 25)


def test_threshold_meanshift_enhance():
    im1 = numpy.zeros((25, 25, 3), numpy.uint8)
    im2 = numpy.zeros((25, 25, 3), numpy.uint8)
    mask = numpy.zeros((25, 25), numpy.uint8)

    mean_im = phm_img.mean_image(list([im1, im2]))

    bin_img = phm_img.threshold_meanshift_enhance(im1, mean_im, mask=mask)
    assert bin_img.shape == (25, 25)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith("test_"):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
