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


from .display_voxel import DisplayVoxel
# ==============================================================================


class DisplayVoxelPointCloud(DisplayVoxel):

    def __init__(self):
        pass

    def show(self, voxel_point_cloud, color=(0, 1, 0)):

        actor = self.vtk_get_actor_from_voxels(
            voxel_point_cloud.voxels_position,
            voxel_point_cloud.voxels_size,
            color=color)

        self.vtk_show_actor([actor])
