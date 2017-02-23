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

from alinea.phenomenal.binarization.morphology import close
# ==============================================================================


def test_wrong_parameters_1():
    try:
        close(None)
    except Exception, e:
        assert e.message == 'image must be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_2():

    image = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        close(image)
    except Exception, e:
        assert e.message == 'image must be 2D array'
        assert type(e) == ValueError
    else:
        assert False


def test_wrong_parameters_3():

    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = 42
    try:
        close(image, mask=mask)
    except Exception, e:
        assert e.message == 'mask must be a numpy.ndarray'
        assert type(e) == TypeError
    else:
        assert False


def test_wrong_parameters_4():

    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25, 3), dtype=numpy.uint8)
    try:
        close(image, mask=mask)
    except Exception, e:
        assert e.message == 'mask must be 2D array'
        assert type(e) == ValueError
    else:
        assert False


def test_simply_working_1():

    image = numpy.zeros((25, 25), dtype=numpy.uint8)
    mask = numpy.zeros((25, 25), dtype=numpy.uint8)

    image_cleaning = close(image, mask=mask)

    assert isinstance(image_cleaning, numpy.ndarray)
    assert image_cleaning.ndim == 2


def test_simply_working_2():
    image = numpy.zeros((25, 25), dtype=numpy.uint8)

    image_cleaning = close(image)

    assert isinstance(image_cleaning, numpy.ndarray)
    assert image_cleaning.ndim == 2

# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
