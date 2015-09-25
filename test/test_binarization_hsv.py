# -*- python -*-
#
#       test_binarization_hsv.py : 
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
#       ========================================================================

#       ========================================================================
#       External Import
import numpy

#       ========================================================================
#       Local Import
import alinea.phenomenal.binarization
import alinea.phenomenal.configuration
import alinea.phenomenal.load_data
import alinea.phenomenal.result_viewer

#       ========================================================================
#       Code


def test_wrong_parameters_1():
    load_configuration = alinea.phenomenal.configuration.loadconfig(
        'configuration_side_image_michael.cfg')
    configuration_side = alinea.phenomenal.configuration.binarization_config(
        load_configuration)

    result = alinea.phenomenal.binarization.binarization(None,
                                                         configuration_side,
                                                         methods='hsv',
                                                         is_top_image=False,
                                                         mean_image=None)
    assert result is None

    image = numpy.zeros((2056, 2056))
    result = alinea.phenomenal.binarization.binarization(image,
                                                         None,
                                                         methods='hsv',
                                                         is_top_image=False,
                                                         mean_image=None)
    assert result is None

    image = numpy.zeros((2056, 2056))
    result = alinea.phenomenal.binarization.binarization(image,
                                                         configuration_side,
                                                         methods='hsv',
                                                         is_top_image=False,
                                                         mean_image=None)
    assert result is None

    image = numpy.zeros((2454, 2056))
    mean_image = numpy.ones((2454, 2056))
    result = alinea.phenomenal.binarization.binarization(image,
                                                         configuration_side,
                                                         methods='hsv',
                                                         is_top_image=False,
                                                         mean_image=mean_image)
    assert result is None


def test_wrong_parameters_2():

    load_configuration = alinea.phenomenal.configuration.loadconfig(
        'configuration_top_image.cfg')
    configuration_top = alinea.phenomenal.configuration.binarization_config(
        load_configuration)

    result = alinea.phenomenal.binarization.binarization(None,
                                                         configuration_top,
                                                         methods='hsv',
                                                         is_top_image=True,
                                                         mean_image=None)
    assert result is None

    image = numpy.zeros((2056, 2056))
    result = alinea.phenomenal.binarization.binarization(image,
                                                         None,
                                                         methods='hsv',
                                                         is_top_image=True,
                                                         mean_image=None)
    assert result is None

    image = numpy.zeros((2056, 2056))
    result = alinea.phenomenal.binarization.binarization(image,
                                                         configuration_top,
                                                         methods='hsv',
                                                         is_top_image=True,
                                                         mean_image=None)
    assert result is None

    image = numpy.zeros((2454, 2056))
    mean_image = numpy.ones((2454, 2056))
    result = alinea.phenomenal.binarization.binarization(image,
                                                         configuration_top,
                                                         methods='hsv',
                                                         is_top_image=True,
                                                         mean_image=None)
    assert result is None


def test_binarization_hsv_1():
    load_configuration = alinea.phenomenal.configuration.loadconfig(
        'configuration_side_image_michael.cfg')
    configuration_side = alinea.phenomenal.configuration.binarization_config(
        load_configuration)

    image = numpy.zeros((2454, 2056, 3), dtype=numpy.uint8)
    result = alinea.phenomenal.binarization.binarization(image,
                                                         configuration_side,
                                                         methods='hsv',
                                                         is_top_image=False,
                                                         mean_image=None)
    assert (result == 0).all()
    assert len(numpy.shape(result)) == 2


def test_binarization_hsv_2():
    load_configuration = alinea.phenomenal.configuration.loadconfig(
        'configuration_top_image.cfg')
    configuration_top = alinea.phenomenal.configuration.binarization_config(
        load_configuration)

    image = numpy.zeros((2454, 2056, 3), dtype=numpy.uint8)
    result = alinea.phenomenal.binarization.binarization(image,
                                                         configuration_top,
                                                         methods='hsv',
                                                         is_top_image=True,
                                                         mean_image=None)
    assert (result == 0).all()
    assert len(numpy.shape(result)) == 2

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_wrong_parameters_1()
    test_wrong_parameters_2()
    test_binarization_hsv_1()
    test_binarization_hsv_2()
