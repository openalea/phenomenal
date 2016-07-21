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

from alinea.phenomenal.data_structure.image3d import Image3D
from alinea.phenomenal.multi_view_reconstruction.routines import remove_internal
# ==============================================================================


def test_simply_working_1():

    image_3d = Image3D.ones((10, 10, 10))

    im = remove_internal(image_3d)

    xx, yy, zz = numpy.where(im)

    # 6 Faces :
    #   -> 10 * 10 * 2  = 200   =>
    #   -> 10 * 8 * 2   = 160   => 200 + 160 + 128 = 488
    #   -> 8 * 8 * 2    = 128   =>
    #
    assert len(xx) == 488


if __name__ == "__main__":
    test_simply_working_1()