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
import os
import time

from alinea.phenomenal.data_structure import (
    VoxelOctree)

from alinea.phenomenal.data_access.plant_1 import (
    plant_1_calibration_camera_side,
    plant_1_images_binarize)

from alinea.phenomenal.multi_view_reconstruction import (
    reconstruction_3d_octree)

from alinea.phenomenal.segmentation_3d import (
    skeletonize_octree,
    labelize_maize_skeleton)

# ==============================================================================

def test_1():
    # images = plant_1_images_binarize()
    # calibration = plant_1_calibration_camera_side()
    #
    # images_and_projections = list()
    # for angle in range(0, 360, 30):
    #     img = images[angle]
    #     function = calibration.get_projection(angle)
    #
    #     images_and_projections.append((img, function))
    #
    # voxels_size = 4
    # # Multi-view reconstruction
    # voxel_octree = reconstruction_3d_octree(
    #     images_and_projections, voxels_size=voxels_size, verbose=True)
    #
    # voxel_octree.write_to_json("test.json")
    # voxel_octree = VoxelOctree.read_from_json("test.json")
    #
    # # show_each_stage_of_octree(voxel_octree)
    # t0 = time.time()
    # voxel_skeleton, voxel_graph = skeletonize_octree(voxel_octree)
    # print time.time() - t0
    # show_voxel_skeleton(voxel_skeleton, with_voxels=True)
    #
    # vsl = labelize_maize_skeleton(voxel_skeleton, voxel_graph)
    # show_voxel_skeleton_labeled(vsl)

    pass

# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
