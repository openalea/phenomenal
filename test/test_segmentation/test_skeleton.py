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
from alinea.phenomenal.data_access import (
    plant_1_voxel_point_cloud)

from alinea.phenomenal.segmentation_3d import (
    skeletonize,
    voxel_graph_from_voxel_point_cloud)
# ==============================================================================


def test_running():

    voxels_size = 8
    vpc = plant_1_voxel_point_cloud(voxels_size=voxels_size)
    voxel_graph = voxel_graph_from_voxel_point_cloud(vpc)
    voxel_skeleton = skeletonize(voxel_graph.graph, voxel_graph.voxels_size)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
