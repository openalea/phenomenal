# -*- python -*-
#
#       test_binarization_adaptive_threshold.py : 
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

#       ========================================================================
#       Code


def test_wrong_parameters():

    factor_side_binarization = \
        alinea.phenomenal.configuration.binarization_factor(
            'factor_image_basic.cfg')

    result = alinea.phenomenal.binarization.binarization(
        None,
        factor_side_binarization,
        methods='adaptive_threshold')
    assert result is None

    images = dict()
    images[0] = numpy.zeros((2056, 2056))
    result = alinea.phenomenal.binarization.binarization(
        images,
        None,
        methods='adaptive_threshold')
    assert result is None

    result = alinea.phenomenal.binarization.binarization(
        dict(),
        factor_side_binarization,
        methods='adaptive_threshold')
    assert len(result) == 0

    images = dict()
    images[0] = numpy.zeros((2056, 2056))
    result = alinea.phenomenal.binarization.binarization(
        images,
        factor_side_binarization,
        methods='adaptive_threshold')
    assert result is None


def test_binarization_adaptive_threshold():
    factor_side_binarization = \
        alinea.phenomenal.configuration.binarization_factor(
            'factor_image_basic.cfg')

    images = dict()
    images[0] = numpy.ones((2454, 2056, 3), dtype=numpy.uint8)
    result = alinea.phenomenal.binarization.binarization(
        images,
        factor_side_binarization,
        methods='adaptive_threshold')

    assert (result[0] == 0).all()
    assert len(numpy.shape(result[0])) == 2


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_wrong_parameters()
    test_binarization_adaptive_threshold()

