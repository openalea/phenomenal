# -*- python -*-
#
#       test_binarization_mean_shift.py :
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


def test_wrong_parameters():
    factor_side_binarization = \
        alinea.phenomenal.configuration.binarization_factor(
            'configuration_image_basic.cfg')

    result = alinea.phenomenal.binarization.binarization(
        None,
        factor_side_binarization,
        methods='mean_shift',
        is_top_image=False,
        mean_image=None)
    assert result is None

    image = numpy.zeros((2056, 2056))
    result = alinea.phenomenal.binarization.binarization(
        image,
        None,
        methods='mean_shift',
        is_top_image=False,
        mean_image=None)
    assert result is None

    image = numpy.zeros((2056, 2056))
    result = alinea.phenomenal.binarization.binarization(
        image,
        factor_side_binarization,
        methods='mean_shift',
        is_top_image=False,
        mean_image=None)
    assert result is None

    image = numpy.zeros((2454, 2056))
    mean_image = numpy.ones((2454, 2056))
    result = alinea.phenomenal.binarization.binarization(
        image,
        factor_side_binarization,
        methods='mean_shift',
        is_top_image=False,
        mean_image=mean_image)
    assert result is None


def test_binarization_mean_shift():
    factor_side_binarization = \
        alinea.phenomenal.configuration.binarization_factor(
            'configuration_image_basic.cfg')

    image = numpy.ones((2454, 2056, 3), dtype=numpy.uint8)
    mean_image = numpy.ones((2454, 2056, 3), dtype=numpy.uint8)
    result = alinea.phenomenal.binarization.binarization(
        image,
        factor_side_binarization,
        methods='mean_shift',
        is_top_image=False,
        mean_image=mean_image)

    assert (result == 0).all()
    assert len(numpy.shape(result)) == 2


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_wrong_parameters()
    test_binarization_mean_shift()
