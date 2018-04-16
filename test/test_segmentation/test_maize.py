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

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.segmentation as phm_seg
# ==============================================================================


def test_maize():

    plant_number = 1
    voxels_size = 16
    voxel_grid = phm_data.voxel_grid(plant_number=plant_number,
                                     voxels_size=voxels_size)

    voxel_graph = phm_seg.voxel_graph_from_voxel_grid(voxel_grid)
    voxel_skeleton = phm_seg.skeletonize(voxel_graph.graph,
                                         voxel_graph.voxels_size)

    vms = phm_seg.maize_segmentation(voxel_skeleton, voxel_graph)
    vmsi = phm_seg.maize_analysis(vms)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
