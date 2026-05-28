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
    calibration = phm_data.load_calibration(data_dir)
    voxel_grid = phm_data.voxel_grid(data_dir, 32)

    # Load images binarize
    graph = phm_seg.graph_from_voxel_grid(voxel_grid)

    voxel_skeleton = phm_seg.skeletonize(voxel_grid, graph)

    image_projection = list()
    for angle in [0, 120, 270]:
        projection = calibration.get_projection("side", angle)
        image_projection.append((bin_images["side"][angle], projection))

    voxel_skeleton = phm_seg.segment_reduction(
        voxel_skeleton, image_projection, required_visible=1, nb_min_pixel=100
    )
