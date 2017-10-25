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
from openalea.phenomenal.segmentation_3D import (
    voxel_graph_from_voxel_grid)

from openalea.phenomenal.data import (
    plant_1_voxel_grid)

# ==============================================================================


def test_graph():

    voxels_size = 8
    vg = plant_1_voxel_grid(voxels_size=voxels_size)

    graph = voxel_graph_from_voxel_grid(vg)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
