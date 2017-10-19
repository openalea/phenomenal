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
import cv2

from skimage.morphology import skeletonize_3d

from openalea.phenomenal.data_access import (
    plant_1_voxel_grid,
    plant_2_voxel_grid,
    plant_1_images_binarize)

from openalea.phenomenal.display import *
from openalea.phenomenal.data_structure import (
    VoxelSkeleton,
    VoxelGrid,
    VoxelSegmentation,
    ImageView)

from openalea.phenomenal.multi_view_reconstruction import *

from openalea.phenomenal.segmentation_3D import (
    voxel_graph_from_voxel_grid,
    skeletonize,
    labelize_maize_skeleton,
    maize_analysis,
    segment_reduction)

from openalea.phenomenal.data_access.plant_1 import (
    plant_1_images_binarize,
    plant_1_calibration_camera_side,
    plant_1_calibration_camera_top)

# ==============================================================================


def routine_select_ref_angle(image_views):

    max_len = 0
    image_view_max = None
    for i, iv in enumerate(image_views):

        x_pos, y_pos, x_len, y_len = cv2.boundingRect(cv2.findNonZero(iv.image))

        if x_len > max_len:
            max_len = x_len
            image_view_max = iv

    image_view_max.ref = True

    return image_views


def main():

    images = plant_1_images_binarize()

    calibration_side = plant_1_calibration_camera_side()
    calibration_top = plant_1_calibration_camera_top()

    # Select images
    image_views = list()
    for angle in range(0, 360, 30):
        projection = calibration_side.get_projection(angle)
        image_views.append(ImageView(images[angle],
                                     projection,
                                     inclusive=False))

    image_views = routine_select_ref_angle(image_views)

    projection = calibration_top.get_projection(0)
    image_views.append(ImageView(images[-1],
                                 projection,
                                 inclusive=True))

    voxels_size = 8
    error_tolerance = 1
    vg = reconstruction_3d(image_views,
                           voxels_size=voxels_size,
                           error_tolerance=error_tolerance,
                           verbose=True)

    vg.voxels_position = map(tuple, list(vg.voxels_position))
    vg.voxels_size = int(vg.voxels_size)

    print len(vg.voxels_position)
    # 27762

    filename = "tmp.npz"
    # vg.write_to_npz(filename)
    vg = VoxelGrid.read_from_npz(filename)
    DisplayVoxelGrid(vg).show()

    import time
    t0 = time.time()

    subgraph = None
    # im = vg.to_image_3d()
    # world_coordinate = im.world_coordinate
    # im = skeletonize_3d(im)
    # vgg = VoxelGrid.from_image_3d(im,
    #                               voxels_size=voxels_size,
    #                               world_coordinate=world_coordinate)
    #
    # subgraph = voxel_graph_from_voxel_grid(vgg).graph
    # DisplayVoxelGrid(vgg).show()

    # vg.voxels_position = list(map(tuple, vg.voxels_position))
    voxel_graph = voxel_graph_from_voxel_grid(vg, connect_all_point=True)
    voxel_skeleton = skeletonize(voxel_graph.graph,
                                 voxel_graph.voxels_size,
                                 subgraph=subgraph)

    # Select images
    image_views = list()
    for angle in range(0, 360, 30):
        projection = calibration_side.get_projection(angle)
        image_views.append(ImageView(images[angle],
                                     projection,
                                     inclusive=False))

    print time.time() - t0, "s"
    t0 = time.time()
    print len(voxel_skeleton.voxel_segments)
    DisplaySkeleton(voxel_skeleton).show()
    voxel_skeleton = segment_reduction(voxel_skeleton,
                                       image_views,
                                       tolerance=4)

    print time.time() - t0, "s"
    print len(voxel_skeleton.voxel_segments)
    DisplaySkeleton(voxel_skeleton).show()

    vms = labelize_maize_skeleton(voxel_skeleton, voxel_graph)
    filename = 'voxel_maize_segmentation.json'
    vms.write_to_json_gz(filename)
    vms = VoxelSegmentation.read_from_json_gz(filename)
    DisplaySegmentation(vms).show()

    vmsi = maize_analysis(vms)
    file_prefix = 'voxel_maize_segmentation_info'
    vmsi.write_to_json_gz(file_prefix)
    vmsi = VoxelSegmentation.read_from_json_gz(file_prefix)

    DisplaySegmentation(vmsi).show(1)


if __name__ == "__main__":
    main()
