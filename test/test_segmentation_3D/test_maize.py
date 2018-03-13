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
from __future__ import division, print_function

from openalea.phenomenal.segmentation_3D import (
    voxel_graph_from_voxel_grid,
    skeletonize,
    maize_segmentation,
    maize_analysis)

from openalea.phenomenal.data import plant_1_voxel_grid


def test_maize():

    voxels_size = 10
    vpc = plant_1_voxel_grid(voxels_size=voxels_size)

    voxel_graph = voxel_graph_from_voxel_grid(vpc)
    voxel_skeleton = skeletonize(voxel_graph.graph,
                                 voxel_graph.voxels_size)

    vms = maize_segmentation(voxel_skeleton, voxel_graph)
    vmsi = maize_analysis(vms)

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()