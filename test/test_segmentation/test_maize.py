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


def test_detect_stem_tip():
    voxel_grid = phm_data.random_voxel_grid(voxels_size=32)

    graph = phm_seg.graph_from_voxel_grid(voxel_grid)
    voxel_skeleton = phm_seg.skeletonize(voxel_grid, graph)
    detection = phm_seg.detect_stem_tip(voxel_skeleton, graph, n_candidates=1)
    assert detection > 0


def test_maize():
    voxel_grid = phm_data.random_voxel_grid(voxels_size=32)

    graph = phm_seg.graph_from_voxel_grid(voxel_grid)

    src_node = tuple(phm_seg.find_base_stem_position(graph.nodes(), 
                                                 voxel_grid.voxels_size, 
                                                 neighbor_size=45))

    voxel_skeleton = phm_seg.skeletonize(voxel_grid, graph, src_node)
    vms = phm_seg.maize_segmentation(voxel_skeleton, graph)
    phm_seg.maize_analysis(vms)

    # Write
    filename = "tmp.json"
    vms.write_to_json_gz(filename)
    phm_obj.VoxelSegmentation.read_from_json_gz(filename)
    os.remove(filename)
