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
from alinea.phenomenal.data_access import plant_1_voxel_point_cloud
from alinea.phenomenal.display import (vtk_show_voxel_points_cloud,
                                       vtk_show_voxel_skeleton,
                                       vtk_show_voxel_maize_segmentation)

from alinea.phenomenal.display.segmentation3d import show_segments

from alinea.phenomenal.data_structure import (VoxelSkeleton)

from alinea.phenomenal.segmentation_3d import (
    voxel_graph_from_voxel_point_cloud,
    skeletonize,
    labelize_maize_skeleton)

# ==============================================================================


def main():

    voxels_size = 16
    vpc = plant_1_voxel_point_cloud(voxels_size=voxels_size)

    vtk_show_voxel_points_cloud(vpc)

    voxel_graph = voxel_graph_from_voxel_point_cloud(vpc)
    voxel_skeleton = skeletonize(voxel_graph.graph,
                                 voxel_graph.voxels_size,
                                 ball_radius=50)

    vtk_show_voxel_skeleton(voxel_skeleton)

    filename = 'voxel_skeleton.json'
    voxel_skeleton.write_to_json(filename)
    voxel_skeleton = VoxelSkeleton.read_from_json(filename)
    vtk_show_voxel_skeleton(voxel_skeleton)

    vms = labelize_maize_skeleton(voxel_skeleton, voxel_graph)

    vtk_show_voxel_maize_segmentation(vms)



if __name__ == "__main__":
    main()
