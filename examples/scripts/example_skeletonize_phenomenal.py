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


from alinea.phenomenal.data_access import (
    plant_1_voxel_point_cloud,
    plant_2_voxel_point_cloud)

from alinea.phenomenal.display import *
from alinea.phenomenal.data_structure import (
    VoxelSkeleton,
    VoxelSegmentation)

from alinea.phenomenal.segmentation_3d import (
    voxel_graph_from_voxel_point_cloud,
    skeletonize,
    labelize_maize_skeleton,
    maize_analysis)

# ==============================================================================


def main():

    voxels_size = 16
    vpc = plant_1_voxel_point_cloud(voxels_size=voxels_size)
    # vpc = plant_2_voxel_point_cloud()
    DisplayVoxelPointCloud().show(vpc)

    voxel_graph = voxel_graph_from_voxel_point_cloud(vpc)
    voxel_skeleton = skeletonize(voxel_graph.graph,
                                 voxel_graph.voxels_size)

    # filename = 'voxel_skeleton.json'
    # voxel_skeleton.write_to_json(filename)
    # voxel_skeleton = VoxelSkeleton.read_from_json(filename)
    DisplayVoxelSkeleton().show(voxel_skeleton)

    vms = labelize_maize_skeleton(voxel_skeleton, voxel_graph)
    # filename = 'voxel_maize_segmentation.json'
    # vms.write_to_json(filename)
    # vms = VoxelSegmentation.read_from_json(filename)
    DisplayVoxelSegmentation().show(vms)

    vmsi = maize_analysis(vms)
    file_prefix = 'voxel_maize_segmentation_info'
    vmsi.write_to_json_gz(file_prefix)
    vmsi = VoxelSegmentation.read_from_json_gz(file_prefix)

    DisplayVoxelSegmentation().show(vmsi)

if __name__ == "__main__":
    main()
