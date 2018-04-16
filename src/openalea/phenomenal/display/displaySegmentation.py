# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import numpy

from ._order_color_map import order_color_map
from .displayVoxel import DisplayVoxel
# ==============================================================================


class DisplaySegmentation(DisplayVoxel):

    def __init__(self):
        DisplayVoxel.__init__(self)

    def __call__(self, voxel_segmentation, mode=1, windows_size=(600, 800)):

        self._voxel_segmentation = voxel_segmentation

        self.show(mode=mode, windows_size=windows_size)

        # self.add_actor_from_voxel_segmentation(self._voxel_segmentation)

    def show(self, mode=1, windows_size=(600, 800)):

        if mode == 1:
            self.display_classic_analysis(self._voxel_segmentation)
        if mode == 2:
            self.display_leaf_split(
                self._voxel_segmentation)
        if mode == 3:
            self.display_leaf_order(self._voxel_segmentation)
        if mode == 4:
            self.display_stem_only(self._voxel_segmentation)
        if mode == 5:
            self.display_skeleton(self._voxel_segmentation)
        if mode == 6:
            self.display_classic_segmentation(self._voxel_segmentation)

        DisplayVoxel.show(self, windows_size=windows_size)

    def record(self, windows_size=(600, 800)):

        DisplayVoxel.show(self, windows_size=windows_size)

    def get_color(self, label, info):

        if label == "stem":
            return 0.5, 0.5, 0.5
        elif label == "unknown":
            return 1, 1, 1
        elif 'pm_leaf_number' in info:
            color_map = order_color_map()
            return color_map[info['pm_leaf_number']]
        else:
            if label == "growing_leaf":
                return 1, 0, 0
            else:
                return None

    def display_skeleton(self, vmsi, order=5):

        for vo in vmsi.get_leafs():
            self.add_actor_from_voxels(
                vo.voxels_position(), vmsi.voxels_size * 0.25, color=(0, 1, 0))

            polyline = vo.get_longest_segment().polyline
            # for vs in vo.voxel_segments:
            self.add_actor_from_voxels(
                polyline, vmsi.voxels_size * 1, color=(1, 0, 0))

            self.add_actor_from_ball_position(
                polyline[0], radius=5, color=(0, 0, 1))

            self.add_actor_from_ball_position(
                polyline[-1], radius=5, color=(1, 0, 0))

        # for vo in vmsi.get_leafs():
        #     if 'order' in vo.info and vo.info['order'] == order:
        #         vs = vo.get_highest_polyline()
        #         self.add_actor_from_voxels(
        #             vs.polyline,
        #             vmsi.voxels_size * 1.5,
        #             color=(0, 0, 1))

    def display_stem_only(self, vmsi):

        for vo in vmsi.voxel_organs:

            color = (0, 1, 0)
            if vo.label == "stem":
                color = (0, 0, 0)

            self.add_actor_from_voxels(
                vo.voxels_position(),
                vmsi.voxels_size,
                color=color)

    def display_classic_segmentation(self, vmsi):

        for vo in vmsi.voxel_organs:
            color = self.get_color(vo.label, vo.info)
            self.add_actor_from_voxels(
                vo.voxels_position(),
                vmsi.voxels_size,
                color=color)

    def display_leaf_order(self, vmsi, leaf_order=4):
        pos_stem = vmsi.get_stem().get_longest_polyline()[-1]

        vo = vmsi.get_leaf_order(leaf_order)

        voxels_position = numpy.array(
            map(tuple, list(vo.voxels_position())))

        pos = vo.info['position_base']
        if vo.label == "growing_leaf":
            pos = pos_stem

            closest_nodes = vo.get_closest_nodes()

            i = vo.get_longest_polyline().index(vo.info['position_base'])

            nodes = list(set.union(*[set(nodes) for nodes in
                                     closest_nodes[0:i]]))

            if len(nodes) > 0:
                voxels = numpy.array(map(tuple, nodes))

                self.add_actor_from_voxels(
                    voxels,
                    vmsi.voxels_size * 0.25,
                    color=(0, 0, 0))

            nodes = list(set.union(*[set(nodes) for nodes in
                                     closest_nodes[i:]]))
            voxels_position = numpy.array(map(tuple, nodes))

        self.add_actor_from_voxels(
            voxels_position,
            vmsi.voxels_size * 0.50,
            color=self.get_color(vo.label, vo.info))

        self.add_actor_from_ball_position(
            vo.info['position_tip'],
            radius=vmsi.voxels_size * 2,
            color=(1, 0, 0))

        self.add_actor_from_ball_position(
            pos, radius=vmsi.voxels_size * 2, color=(0, 0, 1))

        xa, ya, za = pos
        xb, yb, zb = vo.info['vector_mean']
        xc, yc, zc = (xa + xb, ya + yb, za + zb)

        self.add_actor_from_arrow_vector((xa, ya, za),
                                         (xc, yc, zc),
                                         color=(0, 0, 0),
                                         line_width=80)

        xa, ya, za = pos
        xb, yb, zb = vo.info['vector_mean_one_quarter']
        xc, yc, zc = (xa + xb, ya + yb, za + zb)

        self.add_actor_from_arrow_vector((xa, ya, za),
                                         (xc, yc, zc),
                                         color=(0, 0, 1),
                                         line_width=80)

        self.add_actor_from_voxels(
            vo.real_longest_polyline(),
            vmsi.voxels_size * 1,
            color=(1, 0, 0))

        # r, g, b = (0, 0, 1)
        # pos = vo.info['position_tip']
        # pos = (pos[0] - 10, pos[1] - 10, pos[2])
        #
        # if 'order' in vo.info:
        #     order = str(vo.info['order'])
        #     vo.text_actor = self.add_actor_from_text(
        #         order,
        #         position=pos,
        #         scale=40,
        #         color=(r, g, b))
        #
        #     vo.text_actor.SetCamera(self._renderer.GetActiveCamera())

    def display_leaf_split(self, vmsi):

        pos_stem = vmsi.get_stem().get_longest_polyline()[-1]

        for vo in vmsi.voxel_organs:

            voxels_position = numpy.array(
                map(tuple, list(vo.voxels_position())))

            if vo.label == "unknown":
                continue

            if vo.label == "stem":
                self.add_actor_from_voxels(
                    voxels_position,
                    vmsi.voxels_size,
                    color=self.get_color(vo.label, vo.info))

            elif len(vo.voxel_segments) > 0 and "position_tip" in vo.info:

                vm = numpy.array(vo.info['vector_mean'])

                pos = vo.info['position_base']
                if vo.label == "growing_leaf":
                    pos = pos_stem
                    vm = vm * 2

                    closest_nodes = vo.get_closest_nodes()

                    i = vo.get_longest_polyline().index(vo.info['position_base'])

                    v_base = set.union(*[set(nodes) for nodes in
                                         closest_nodes[:i]])

                    v_leaf = set.union(*[set(nodes) for nodes in
                                         closest_nodes[i:]])

                    v_base = v_base - v_leaf
                    if len(v_base) > 0:
                        voxels = numpy.array(map(tuple, list(v_base)))

                        self.add_actor_from_voxels(
                            voxels + vm,
                            vmsi.voxels_size * 0.20,
                            color=(0, 0, 0))

                    voxels_position = numpy.array(map(tuple, list(v_leaf)))

                self.add_actor_from_voxels(
                        voxels_position + vm,
                        vmsi.voxels_size,
                        color=self.get_color(vo.label, vo.info))

                self.add_actor_from_ball_position(
                    vo.info['position_tip'] + vm,
                    radius=vmsi.voxels_size * 2,
                    color=(1, 0, 0))

                self.add_actor_from_ball_position(
                    pos + vm, radius=vmsi.voxels_size * 2, color=(0, 0, 1))

                xa, ya, za = pos
                xb, yb, zb = tuple(vm)
                xc, yc, zc = (xa + xb, ya + yb, za + zb)

                self.add_actor_from_arrow_vector((xa, ya, za),
                                                 (xc, yc, zc),
                                                 color=(0, 0, 0),
                                                 line_width=40)

                r, g, b = (0, 0, 1)
                pos = vo.info['position_tip'] + vm
                pos = (pos[0] - 10, pos[1] - 10, pos[2])

                if 'order' in vo.info:
                    order = str(vo.info['order'])
                    vo.text_actor = self.add_actor_from_text(
                        order,
                        position=pos,
                        scale=40,
                        color=(r, g, b))

                    vo.text_actor.SetCamera(self._renderer.GetActiveCamera())

    def display_classic_analysis(self, vmsi):

        def plot(vo):
            if vo is None:
                return

            voxels_position = numpy.array(
                map(tuple, list(vo.voxels_position())))

            self.add_actor_from_voxels(
                voxels_position,
                vmsi.voxels_size,
                color=self.get_color(vo.label, vo.info))

            if ((vo.label == "mature_leaf" or vo.label == "growing_leaf") and
                    len(vo.voxel_segments) > 0 and "pm_position_tip" in
                vo.info):

                pos = vo.info['pm_position_base']

                self.add_actor_from_ball_position(
                    vo.info['pm_position_tip'],
                    radius=vmsi.voxels_size * 2,
                    color=(1, 0, 0))

                self.add_actor_from_ball_position(
                    pos, radius=vmsi.voxels_size * 2, color=(0, 0, 1))

                r, g, b = (0, 0, 1)
                pos = vo.info['pm_position_tip']
                pos = (pos[0] - 10, pos[1] - 10, pos[2])

                # if 'pm_leaf_number' in vo.info:
                #     order = str(vo.info['pm_leaf_number'])
                #     vo.text_actor = self.add_actor_from_text(
                #         order,
                #         position=pos,
                #         scale=40,
                #         color=(r, g, b))
                #
                #     vo.text_actor.SetCamera(self._renderer.GetActiveCamera())

        # plot(vmsi.get_unknown())
        for vo in vmsi.get_leafs():
            plot(vo)
        plot(vmsi.get_stem())

    def record(self, list_vmsi, filename):

        func = lambda vmsi: self.display_classic_analysis(vmsi)
        self.record_video(filename, list_vmsi, func)



