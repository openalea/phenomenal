# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

from .displayVoxel import DisplayVoxel
# ==============================================================================


class DisplaySkeleton(DisplayVoxel):

    def __init__(self):
        DisplayVoxel.__init__(self)

    def __call__(self,
                 voxel_skeleton,
                 with_voxel=True,
                 voxel_color=(0, 1, 0),
                 skeleton_color=(1, 0, 0),
                 color_segment=None):

        self.add_actor_voxel_skeleton(voxel_skeleton,
                                      with_voxel=with_voxel,
                                      voxel_color=voxel_color,
                                      skeleton_color=skeleton_color,
                                      color_segment=color_segment)

        self.show()

    def add_actor_voxel_skeleton(self,
                                 voxel_skeleton,
                                 with_voxel=False,
                                 voxel_color=(0, 1, 0),
                                 skeleton_color=(1, 0, 0),
                                 color_segment=None):

        orderer_voxel_segments = sorted(voxel_skeleton.voxel_segments,
                                        key=lambda vs: len(vs.voxels_position))

        for i, vs in enumerate(orderer_voxel_segments):

            if color_segment is not None and color_segment == i:
                self.add_actor_from_voxels(
                    vs.voxels_position,
                    voxel_skeleton.voxels_size * 0.50,
                    color=(0, 0, 1))
            elif with_voxel:
                self.add_actor_from_voxels(
                    vs.voxels_position,
                    voxel_skeleton.voxels_size * 0.15,
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

