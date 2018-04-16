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

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.object as phm_obj
# ==============================================================================


def test_read_write():

    plant_number = 1
    voxels_size = 8
    voxel_grid = phm_data.voxel_grid(plant_number=plant_number,
                                     voxels_size=voxels_size)

    filename = 'test.npz'
    voxel_grid.write_to_npz(filename)
    vg = phm_obj.VoxelGrid.read_from_npz(filename)
    os.remove(filename)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
