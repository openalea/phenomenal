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


import os

import cv2
import numpy
import pytest

import openalea.phenomenal.image as phm_img
# ==============================================================================


def test_1():
    im1 = numpy.zeros((400, 400))
    im1[10:-10, 10:-10] = 255

    phm_img.write_image("tmp.png", im1)
    im2 = phm_img.read_image("tmp.png", "L")

    assert numpy.array_equal(im1, im2)

    # delete the tmp file
    os.remove("tmp.png")


def test_rgb_round_trip_and_order(tmp_path):
    # pure red in RGB order
    rgb = numpy.zeros((20, 30, 3), dtype=numpy.uint8)
    rgb[..., 0] = 255
    path = tmp_path / "red.png"
    phm_img.write_image(path, rgb)

    assert numpy.array_equal(phm_img.read_image(path), rgb)
    assert numpy.array_equal(phm_img.read_image(path, "RGB"), rgb)
    gray = phm_img.read_image(path, "L")
    assert gray.shape == (20, 30)
    # the file itself is a standard image: OpenCV reads it as red (BGR order)
    assert (cv2.imread(str(path))[..., 2] == 255).all()


def test_read_bgr_file_as_rgb(tmp_path):
    bgr = numpy.zeros((10, 10, 3), dtype=numpy.uint8)
    bgr[..., 0] = 200  # blue in OpenCV's BGR order
    path = tmp_path / "blue.png"
    cv2.imwrite(str(path), bgr)

    rgb = phm_img.read_image(path, "RGB")
    assert (rgb[..., 2] == 200).all() and (rgb[..., 0] == 0).all()


def test_non_ascii_path(tmp_path):
    image = numpy.full((5, 5), 128, dtype=numpy.uint8)
    path = tmp_path / "données" / "été.png"
    phm_img.write_image(path, image)
    assert numpy.array_equal(phm_img.read_image(path, "L"), image)


def test_read_image_errors(tmp_path):
    with pytest.raises(ValueError):
        phm_img.read_image(tmp_path / "x.png", "HSV")
    path = tmp_path / "not_an_image.png"
    path.write_text("not an image")
    with pytest.raises(IOError):
        phm_img.read_image(path)
