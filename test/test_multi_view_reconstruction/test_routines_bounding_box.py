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

import openalea.phenomenal.object as phm_obj
# ==============================================================================


def test_simply_working_1():

    voxels_position = list()
    voxels_position.append((0, 0, 0))
    voxels_position.append((10, 10, 10))
    voxels_size = 1
    vpc = phm_obj.VoxelGrid(voxels_position, voxels_size)
    pt_min, pt_max = vpc.bounding_box()

    assert pt_min == (0, 0, 0)
    assert pt_max == (10, 10, 10)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
