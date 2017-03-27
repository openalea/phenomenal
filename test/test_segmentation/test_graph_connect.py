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
import networkx
import numpy
import time

from alinea.phenomenal.segmentation_3d import (
    voxel_graph_from_voxel_point_cloud)

from alinea.phenomenal.data_access import (
    plant_1_voxel_point_cloud)

from alinea.phenomenal.segmentation_3d import (
    create_graph,
    connect_all_node_with_nearest_neighbors)
# ==============================================================================

def test_():

    voxels_size = 8
    vpc = plant_1_voxel_point_cloud(voxels_size=voxels_size)
    graph = create_graph(vpc.voxels_position, vpc.voxels_size)
    graph = connect_all_node_with_nearest_neighbors(graph)



if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
