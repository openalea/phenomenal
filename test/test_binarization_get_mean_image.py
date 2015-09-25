# -*- python -*-
#
#       test_binarization_get_mean_image.py :
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


#       ========================================================================
#       Code


def test_wrong_parameters():
    result = alinea.phenomenal.binarization.get_mean_image(None)
    assert result is None

    result = alinea.phenomenal.binarization.get_mean_image([])
    assert result is None

    result = alinea.phenomenal.binarization.get_mean_image([[]])
    assert result is None

    image = numpy.zeros((1, 1))
    result = alinea.phenomenal.binarization.get_mean_image(image)
    assert result is None

    image = numpy.zeros((2454, 2056))
    result = alinea.phenomenal.binarization.get_mean_image(image)
    assert result is None

    images = list()
    for i in range(0, 1):
        images.append(numpy.ones((2056, 2056)))
    for i in range(1, 10):
        images.append(numpy.zeros((205, 205)))
    image = alinea.phenomenal.binarization.get_mean_image(images)
    assert image is None


def test_out_value():
    images = list()
    for i in range(10):
        images.append(numpy.zeros((2056, 2056)))

    image = alinea.phenomenal.binarization.get_mean_image(images)
    assert numpy.count_nonzero(image) == 0
    assert numpy.shape(image) == (2056, 2056)

    #   ========================================================================

    images = list()
    for i in range(10):
        images.append(numpy.ones((2056, 2056)))

    image = alinea.phenomenal.binarization.get_mean_image(images)
    assert numpy.shape(image) == (2056, 2056)
    assert numpy.count_nonzero(image) == 2056*2056

    #   ========================================================================

    images = list()
    for i in range(0, 1):
        images.append(numpy.ones((2056, 2056)))
    for i in range(1, 10):
        images.append(numpy.zeros((2056, 2056)))

    image = alinea.phenomenal.binarization.get_mean_image(images)
    assert (image == 0.1).all()


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_wrong_parameters()
    test_out_value()

