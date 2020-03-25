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

import os
import numpy.random
import openalea.phenomenal.data as phm_data
import openalea.phenomenal.object as phm_obj
# ==============================================================================


def test_read_write():

    voxels_size = 16
    voxels_position = numpy.array(list(numpy.ndindex((10, 15, 5)))) * 16
    src_vg = phm_obj.VoxelGrid(voxels_position, voxels_size)

    filename = 'test.npz'
    src_vg.write_to_npz(filename)
    dist_vg = phm_obj.VoxelGrid.read_from_npz(filename)
    os.remove(filename)

    assert src_vg.voxels_size == dist_vg.voxels_size
    assert (src_vg.voxels_position == dist_vg.voxels_position).all()


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
