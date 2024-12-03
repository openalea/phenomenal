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
import os

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.calibration as phm_calib
# ==============================================================================


def test_chessboard_1():
    chess = phm_calib.Chessboard(50, (8, 6))

    assert chess.square_size == 50
    assert chess.shape == (8, 6)
    assert chess.image_points == dict()


def test_chessboard_2():
    chess = phm_calib.Chessboard(50, (8, 6))

    result = chess.get_corners_local_3d(old_style=True)

    assert numpy.array_equal(result[8 * 0 + 0], [0.0, 0.0, 0.0])
    assert numpy.array_equal(result[8 * 0 + 1], [50.0, 0.0, 0.0])
    assert numpy.array_equal(result[8 * 0 + 2], [100.0, 0.0, 0.0])
    assert numpy.array_equal(result[8 * 0 + 3], [150.0, 0.0, 0.0])
    assert numpy.array_equal(result[8 * 0 + 4], [200.0, 0.0, 0.0])
    assert numpy.array_equal(result[8 * 0 + 5], [250.0, 0.0, 0.0])
    assert numpy.array_equal(result[8 * 0 + 6], [300.0, 0.0, 0.0])
    assert numpy.array_equal(result[8 * 0 + 7], [350.0, 0.0, 0.0])

    assert numpy.array_equal(result[8 * 5 + 0], [0.0, 250.0, 0.0])
    assert numpy.array_equal(result[8 * 5 + 1], [50.0, 250.0, 0.0])
    assert numpy.array_equal(result[8 * 5 + 2], [100.0, 250.0, 0.0])
    assert numpy.array_equal(result[8 * 5 + 3], [150.0, 250.0, 0.0])
    assert numpy.array_equal(result[8 * 5 + 4], [200.0, 250.0, 0.0])
    assert numpy.array_equal(result[8 * 5 + 5], [250.0, 250.0, 0.0])
    assert numpy.array_equal(result[8 * 5 + 6], [300.0, 250.0, 0.0])
    assert numpy.array_equal(result[8 * 5 + 7], [350.0, 250.0, 0.0])


def test_chessboard_3():
    chess = phm_calib.Chessboard(50, (8, 6))

    dir_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "../data/plant_1"
    )
    images = phm_data.chessboard_images(dir_path)[0]
    found = chess.detect_corners("side", 42, images["side"][42], check_order=False)

    if found:
        corners = chess.get_corners_2d("side")[42]
        res = numpy.array(corners).astype(float)
        res = numpy.around(res, decimals=2)

        assert res.shape == (48, 2)
    else:
        assert False


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith("test_"):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
