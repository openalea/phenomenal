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
import os

from openalea.phenomenal.data_access import plant_1_voxel_grid
from openalea.phenomenal.data_structure import VoxelGrid, Image3D
# ==============================================================================


def test_read_write():

    voxels_size = 8
    vpc = plant_1_voxel_grid(voxels_size)

    filename = 'test.npz'
    vpc.write_to_npz(filename)
    vg = VoxelGrid.read_from_npz(filename)
    os.remove(filename)


# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
