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
from skimage.morphology import skeletonize_3d

from alinea.phenomenal.display import (
    show_voxel_point_cloud)

from alinea.phenomenal.data_structure import (
    voxels_position_to_image_3d,
    image_3d_to_voxels_position,
    VoxelGrid)
# ==============================================================================

from alinea.phenomenal.data_access import plant_1_voxel_centers
# ==============================================================================


def main():

    voxels_size = 4
    voxels_position = plant_1_voxel_centers(voxel_size=voxels_size)

    vpc = VoxelGrid(voxels_position, voxels_size)
    show_voxel_point_cloud(vpc,
                           size=(5000, 5000),
                           color=(0.1, 0.9, 0.1),
                           azimuth=310,
                           distance=3000,
                           elevation=90,
                           focalpoint=(0, 0, 200))

    im = voxels_position_to_image_3d(voxels_position, voxels_size)
    world_coordinate = im.world_coordinate
    im = skeletonize_3d(im)

    voxels_position, voxels_size = image_3d_to_voxels_position(
        im,
        voxels_size=voxels_size,
        world_coordinate=world_coordinate)

    vpc = VoxelGrid(voxels_position, voxels_size)
    show_voxel_point_cloud(vpc,
                           size=(5000, 5000),
                           color=(0.9, 0.1, 0.1),
                           azimuth=310,
                           distance=3000,
                           elevation=90,
                           focalpoint=(0, 0, 200))


if __name__ == "__main__":
    main()
