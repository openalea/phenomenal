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
from alinea.phenomenal.data_access import plant_1_voxel_centers
from alinea.phenomenal.display import (
    show_voxels)

from alinea.phenomenal.display.segmentation3d import show_segments
from alinea.phenomenal.segmentation_3d.skeleton import skeletonize

# ==============================================================================


def main():

    voxels_size = 16

    voxels_center = plant_1_voxel_centers(voxel_size=voxels_size)

    show_voxels(voxels_center, voxels_size,
                   color=(0.1, 0.9, 0.1),
                   size=(5000, 5000),
                   azimuth=310,
                   distance=3000,
                   elevation=90,
                   focalpoint=(0, 0, 200))

    segments, graph = skeletonize(voxels_center, voxels_size)

    show_segments(segments, voxels_size,
                  with_voxels=True,
                  size=(5000, 5000),
                  azimuth=310,
                  distance=3000,
                  elevation=90,
                  focalpoint=(0, 0, 200))


if __name__ == "__main__":
    main()
