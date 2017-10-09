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
from .displayVoxel import DisplayVoxel
# ==============================================================================


class DisplaySkeleton(DisplayVoxel):

    def __init__(self, voxel_skeleton,
                 with_voxel=True,
                 voxel_color=(0, 1, 0),
                 skeleton_color=(1, 0, 0)):

        DisplayVoxel.__init__(self)

        for vs in voxel_skeleton.voxel_segments:

            if with_voxel:
                self.add_actor_from_voxels(
                    vs.voxels_position,
                    voxel_skeleton.voxels_size * 0.50,
                    color=voxel_color)

            self.add_actor_from_voxels(
                vs.polyline,
                voxel_skeleton.voxels_size * 1.5,
                color=skeleton_color)

            self.add_actor_from_ball_position(vs.polyline[0],
                                              radius=10,
                                              color=(0, 0, 1))

            self.add_actor_from_ball_position(vs.polyline[-1],
                                              radius=10,
                                              color=(1, 0, 0))

