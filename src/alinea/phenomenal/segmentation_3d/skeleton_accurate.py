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
import networkx

from alinea.phenomenal.data_structure import (
    VoxelPointCloud)

from alinea.phenomenal.multi_view_reconstruction import (
    reconstruction_3d)

from alinea.phenomenal.segmentation_3d import (
    voxel_graph_from_voxel_point_cloud,
    compute_all_shorted_path)

# ==============================================================================


def skeletonize_accurate(voxel_skeleton, images_projection, accurate):

    for voxel_segment in voxel_skeleton.voxel_segments:
        voxels_position = voxel_segment.voxels_position
        voxels_size = voxel_segment.voxels_position

        voxels_position = reconstruction_3d(images_projection,
                                            voxels_size=accurate,
                                            origin_voxels_size=voxels_size)

        vpc = VoxelPointCloud(voxels_position, accurate)

        voxel_graph = voxel_graph_from_voxel_point_cloud(vpc)

        all_shorted_path_to_stem_base = compute_all_shorted_path(
            voxel_graph.graph, voxel_graph.voxels_size)

        print type(all_shorted_path_to_stem_base)