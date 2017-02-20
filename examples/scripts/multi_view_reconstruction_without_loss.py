# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
from __future__ import print_function, division

import mayavi.mlab

from alinea.phenomenal.data_structure import VoxelPointCloud

from alinea.phenomenal.display import (
    plot_voxels,
    plot_list_voxels,
    )

from alinea.phenomenal.multi_view_reconstruction import (
    read_from_xyz)

from alinea.phenomenal.segmentation_3d.maize import (
    maize_plant_segmentation)

from alinea.phenomenal.segmentation_3d.format import (
    write_labeled_skeleton_path_to_csv,
    write_labeled_voxels_to_csv)

from alinea.phenomenal.segmentation_3d.skeleton import (
    skeletonize)

from alinea.phenomenal.display import (
    show_segment_voxel, show_voxel_point_cloud_segments, show_list_points_3d,
    show_voxel_point_cloud_segments_2, show_voxel_point_cloud_segments_3)

from alinea.phenomenal.data_structure.voxelPointCloudSegments import (
    VoxelPointCloudSegments)


from alinea.phenomenal.display.multi_view_reconstruction import (
    show_voxel_point_cloud)

from alinea.phenomenal.data_access import (
    plant_1_calibration_camera_side,
    plant_1_images_binarize)

from alinea.phenomenal.multi_view_reconstruction.\
    multi_view_reconstruction_without_loss import (reconstruction_without_loss)

from alinea.phenomenal.data_structure import VoxelPointCloud

from alinea.phenomenal.display.multi_view_reconstruction import (
    show_voxel_point_cloud)

# ==============================================================================

def show_segments(sements):
    mayavi.mlab.figure()

    voxels = set().union(*[voxel for voxel, path in sements])
    paths = set().union(*[path for voxel, path in sements])

    # plot_list_points_3d([voxels],
    #                     list_color=[(0, 1, 0)])

    plot_list_points_3d([paths],
                        list_color=[(1, 0, 0)],
                        scale_factor=2)

    print("Number of segment detected : ", len(sements))

    mayavi.mlab.show()

# ==============================================================================


images = plant_1_images_binarize()
calibration = plant_1_calibration_camera_side()

images_projections_refs = list()
for angle in range(0, 360, 30):
    img = images[angle]
    function = calibration.get_projection(angle)

    ref = False
    if angle == 120:
        ref = True
    images_projections_refs.append((img, function, ref))

# ==============================================================================

# voxel_size = 4
# voxel_centers = reconstruction_without_loss(images_projections_refs,
#                                 voxel_size=voxel_size,
#                                 error_tolerance=1,
#                                 verbose=True)
#
# filename = "4_without_loss.json"
#
# # vpc = VoxelPointCloud(voxel_centers, voxel_size)
# # vpc.write_to_json(filename)
#
# vpc = VoxelPointCloud.read_from_json(filename)
#
# voxels_center = vpc.voxels_center
# voxels_size = vpc.voxels_size
#
#
# # ==============================================================================
# show_voxel_point_cloud(vpc, color=(0.1, 0.8, 0.1))
#
# segments, graph = skeletonize(voxels_center, voxels_size)
# show_segments(segments)
#
# for voxels, path in segments:
#     plot_list_points_3d([voxels])
#
# for voxels, path in segments:
#     plot_points_3d(path, color=(0, 0, 0))
#
# mayavi.mlab.show()
#
# vpcs = maize_plant_segmentation(segments, voxels_size, graph)

filename_output = "truck.json"
# vpcs.write_to_json(filename_output)
vpcs = VoxelPointCloudSegments.read_from_json(filename_output)
show_voxel_point_cloud_segments_2(vpcs)