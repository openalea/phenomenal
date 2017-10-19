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

from openalea.phenomenal.display import (
    DisplayVoxelGrid)

from openalea.phenomenal.data_structure import (
    VoxelGrid)
# ==============================================================================

from openalea.phenomenal.data_access import plant_1_voxel_grid
# ==============================================================================


def main():

    voxels_size = 4
    vg = plant_1_voxel_grid(voxels_size=voxels_size)
    DisplayVoxelGrid(vg).show()

    im = vg.to_image_3d()
    world_coordinate = im.world_coordinate
    im = skeletonize_3d(im)
    vg = VoxelGrid.from_image_3d(im,
                                 voxels_size=voxels_size,
                                 world_coordinate=world_coordinate)
    DisplayVoxelGrid(vg).show()


if __name__ == "__main__":
    main()
