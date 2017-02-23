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
    compute_all_shorted_path,
    skeletonize)

# ==============================================================================


def skeletonize_octree(voxel_octree,
                       voxels_size_to_skeletonize=16,
                       distance_planes=1,
                       voxels_size_output=4):

    vpc = voxel_octree.get_voxel_point_cloud(voxels_size_to_skeletonize)

    voxel_graph = voxel_graph_from_voxel_point_cloud(vpc)

    voxel_skeleton = skeletonize(voxel_graph.graph, voxel_graph.voxels_size,
                                 distance_plane=distance_planes)

    for voxel_segment in voxel_skeleton.voxel_segments:
        voxels_position = voxel_segment.voxels_position



