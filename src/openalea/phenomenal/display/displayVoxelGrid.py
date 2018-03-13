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
from __future__ import division, print_function, absolute_import

from .displayVoxel import DisplayVoxel
# ==============================================================================


class DisplayVoxelGrid(DisplayVoxel):

    def __init__(self):
        DisplayVoxel.__init__(self)

    def __call__(self, voxel_grid, color=(0, 0.8, 0)):

        self.add_actor_from_voxels(
            voxel_grid.voxels_position,
            voxel_grid.voxels_size,
            color=color)

        self.show()

    def record(self, list_voxel_grid, filename, color=(0, 0.8, 0)):

        func = lambda vg: self.add_actor_from_voxels(vg.voxels_position,
                                                     vg.voxels_size,
                                                     color=color)
        self.set_camera(elevation=20)
        self.record_video(filename, list_voxel_grid, func)