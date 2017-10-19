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

    def __init__(self, voxel_grid, color=(0, 0.8, 0)):
        DisplayVoxel.__init__(self)

        self.add_actor_from_voxels(
            voxel_grid.voxels_position,
            voxel_grid.voxels_size,
            color=color)

