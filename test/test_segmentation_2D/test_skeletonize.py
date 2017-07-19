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
from alinea.phenomenal.segmentation_2d import skeletonize

import numpy


def test_skeletonize_thinning():
    image = numpy.zeros((99, 101))
    image[20:40, 20:40] = 255

    ske = skeletonize(image, methods='thinning')
    assert ske.shape == image.shape
    assert numpy.count_nonzero(ske) > 0

    ske = skeletonize(image, methods='erode_dilate')
    assert ske.shape == image.shape
    assert numpy.count_nonzero(ske) > 0

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()