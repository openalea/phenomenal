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

import openalea.phenomenal.object as phm_obj
import openalea.phenomenal.segmentation as phm_seg
# ==============================================================================


def test_simply_working_1():

    image_3d = phm_obj.Image3D.ones((10, 10, 10))
    im = phm_seg.remove_internal(image_3d)

    xx, yy, zz = numpy.where(im)

    # 6 Faces :
    #   -> 10 * 10 * 2  = 200   =>
    #   -> 10 * 8 * 2   = 160   => 200 + 160 + 128 = 488
    #   -> 8 * 8 * 2    = 128   =>
    assert len(xx) == 488


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
