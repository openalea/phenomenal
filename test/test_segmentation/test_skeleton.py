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
import openalea.phenomenal.segmentation as phm_seg

from pathlib import Path
test_subdir = Path(__file__).parent if '__file__' in globals() else Path(".").resolve()
data_dir = test_subdir.parent / "data" / "plant_1"

# ==============================================================================


def test_running():
    bin_images = phm_data.bin_images(data_dir)
    calibrations = phm_data.calibrations(data_dir)
    voxel_grid = phm_data.voxel_grid(data_dir, 32)

    # Load images binarize
    graph = phm_seg.graph_from_voxel_grid(voxel_grid)
    src_node = tuple(phm_seg.find_base_stem_position(graph.nodes(), 
                                                 voxel_grid.voxels_size, 
                                                 neighbor_size=45))

    voxel_skeleton = phm_seg.skeletonize(voxel_grid, graph, src_node)

    image_projection = list()
    for angle in [0, 120, 270]:
        projection = calibrations["side"].get_projection(angle)
        image_projection.append((bin_images["side"][angle], projection))

    voxel_skeleton = phm_seg.segment_reduction(
        voxel_skeleton, image_projection, required_visible=1, nb_min_pixel=100
    )
