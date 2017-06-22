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

import vtk
import random

from ._order_color_map import order_color_map
from .display_voxel import DisplayVoxel
# ==============================================================================


class DisplayVoxelSkeleton(DisplayVoxel):

    def __init__(self):
        pass

    def show(self, voxel_skeleton, color=None):

        actors = list()

        for vs in voxel_skeleton.voxel_segments:
            actor_voxels = self.vtk_get_actor_from_voxels(
                vs.voxels_position,
                voxel_skeleton.voxels_size * 0.25)

            actors.append(actor_voxels)

            actor_polyline = self.vtk_get_actor_from_voxels(
                vs.polyline, voxel_skeleton.voxels_size, color=(0, 0, 0))

            actors.append(actor_polyline)

        self.vtk_show_actor(actors)
