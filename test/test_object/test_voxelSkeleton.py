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
import os

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.object as phm_obj
import openalea.phenomenal.segmentation as phm_seg
# ==============================================================================


def test_readwrite():
    voxel_grid = phm_data.random_voxel_grid(voxels_size=32)
    graph = phm_seg.graph_from_voxel_grid(voxel_grid)
    src_vsk = phm_seg.skeletonize(voxel_grid, graph)
    filename = "test.json.gz"
    src_vsk.write_to_json_gz(filename)
    dst_vsk = phm_obj.VoxelSkeleton.read_from_json_gz(filename)
    os.remove(filename)

    assert src_vsk.voxels_size == dst_vsk.voxels_size
    for src_seg, dst_seg in zip(src_vsk.segments, dst_vsk.segments):
        assert src_seg.voxels_position == dst_seg.voxels_position
        assert src_seg.polyline == dst_seg.polyline
        for src_nodes, dst_nodes in zip(src_seg.closest_nodes, dst_seg.closest_nodes):
            assert src_nodes == dst_nodes
