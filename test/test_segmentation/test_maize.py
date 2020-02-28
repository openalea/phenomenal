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
import openalea.phenomenal.segmentation as phm_seg
# ==============================================================================


def test_maize():

    voxel_grid = phm_data.random_voxel_grid(voxels_size=32)

    graph = phm_seg.graph_from_voxel_grid(voxel_grid)
    voxel_skeleton = phm_seg.skeletonize(voxel_grid, graph)
    vms = phm_seg.maize_segmentation(voxel_skeleton, graph)
    vmsi = phm_seg.maize_analysis(vms)

    # Write
    filename = 'tmp.json'
    vms.write_to_json_gz(filename)
    vms = phm_obj.VoxelSegmentation.read_from_json_gz(filename)
    os.remove(filename)

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
