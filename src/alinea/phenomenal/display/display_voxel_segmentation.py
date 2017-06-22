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


class DisplayVoxelSegmentation(DisplayVoxel):

    def __init__(self):
        pass

    def get_color(self, label, info):

        if label == "stem":
            return 0.5, 0.5, 0.5
        elif label == "unknown":
            return 1, 1, 1
        elif 'order' in info:
            color_map = order_color_map()
            return color_map[info['order']]
        else:
            if label == "cornet_leaf":
                return 1, 0, 0
            else:
                return None

    def vtk_build_actor_maize_segmentation_info(self, vmsi):

        actors = list()

        for vo in vmsi.voxel_organs:

            actor_voxels = self.vtk_get_actor_from_voxels(
                vo.voxels_position(),
                vmsi.voxels_size,
                color=self.get_color(vo.label, vo.info))

            actors.append(actor_voxels)

            if (vo.label != "unknown" and len(vo.voxel_segments) > 0 and
                        "position_tip" in vo.info):
                actor_position_tip = self.vtk_get_ball_actor_from_position(
                    vo.info['position_tip'],
                    radius=vmsi.voxels_size * 2,
                    color=(1, 0, 0))
                actors.append(actor_position_tip)

                actor_position_base = self.vtk_get_ball_actor_from_position(
                    vo.info['position_base'],
                    radius=vmsi.voxels_size * 2,
                    color=(0, 0, 1))

                actors.append(actor_position_base)

                xa, ya, za = vo.info['position_base']
                xb, yb, zb = vo.info['vector_mean']
                xc, yc, zc = (xa + xb, ya + yb, za + zb)

                actor_arrow = self.vtk_get_arrow_vector((xa, ya, za),
                                                        (xc, yc, zc),
                                                        color=(1, 1, 1))

                actors.append(actor_arrow)

                # r, g, b = (0, 0, 1)
                # pos = vo.info['position_tip']
                # pos = (pos[0] - 10, pos[1] - 10, pos[2])
                # vo.text_actor = vtk_get_text_actor(
                #     vo.label,
                #     position=pos,
                #     scale=40,
                #     color=(r, g, b))
                #
                # actors.append(vo.text_actor)
                #
                # vo.text_actor.SetCamera(self.ren.GetActiveCamera())

        return actors

    def show(self, voxel_segmentation, color=None):

        actors = self.vtk_build_actor_maize_segmentation_info(
            voxel_segmentation)

        self.vtk_show_actor(actors)

    def save_render(self, voxel_segmentation, file_prefix, suffix='.x3d'):
        actors = self.vtk_build_actor_maize_segmentation_info(
            voxel_segmentation)

        if suffix == ".x3d":
            self.vtk_save_actors_scene_to_x3d(actors, file_prefix)
        elif suffix == ".wrl":
            self.vtk_save_actors_scene_to_vrml(actors, file_prefix)
        else:
            raise ValueError