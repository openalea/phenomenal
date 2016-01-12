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

from alinea.phenomenal.binarization import top_binarization_hsv
from alinea.phenomenal.configuration import binarization_factor
# ==============================================================================


def test_wrong_parameters_1():

    factor_side_binarization = binarization_factor('factor_image_basic.cfg')

    try:
        top_binarization_hsv(None, factor_side_binarization)
    except Exception, e:
        assert e.message == 'image should be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_2():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)

    try:
        top_binarization_hsv(image, None)
    except Exception, e:
        assert e.message == 'factor should be a BinarizationFactor object'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_3():

    factor_side_binarization = binarization_factor('factor_image_basic.cfg')
    image = numpy.zeros((25, 25), dtype=numpy.uint8)

    try:
        top_binarization_hsv(image, factor_side_binarization)
    except Exception, e:
        assert e.message == 'image should be 3D array'
        assert type(e) == ValueError
    else:
        print False


def test_top_binarization_hsv_1():

    factor_side_binarization = binarization_factor('factor_image_basic.cfg')
    image = numpy.zeros((2454, 2056, 3), dtype=numpy.uint8)

    binarize_image = top_binarization_hsv(
        image, factor_side_binarization)

    assert (binarize_image == 0).all()
    assert binarize_image.ndim == 2
    assert binarize_image.shape == (2454, 2056)


# ==============================================================================

if __name__ == "__main__":
    test_wrong_parameters_1()
    test_wrong_parameters_2()
    test_wrong_parameters_3()

    test_top_binarization_hsv_1()
