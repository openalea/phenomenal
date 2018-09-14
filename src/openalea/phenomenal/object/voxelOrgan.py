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

from .voxelSegment import VoxelSegment
# ==============================================================================


class VoxelOrgan(object):

    def __init__(self, label, sub_label=None):
        self.voxel_segments = list()
        self.label = label
        self.sub_label = sub_label
        self.info = dict()

    def add_voxel_segment(self, voxels_position, polyline, closest_nodes=None):
        self.voxel_segments.append(VoxelSegment(polyline, voxels_position, closest_nodes))

    def voxels_position(self):

        voxels_position = set()
        for voxel_segment in self.voxel_segments:
            voxels_position = voxels_position.union(
                voxel_segment.voxels_position)

        return voxels_position

    # ==========================================================================

    def get_longest_segment(self):
        longest_polyline = list()
        longest_segment = None

        for vs in self.voxel_segments:
            if len(vs.polyline) > len(longest_polyline):
                longest_polyline = vs.polyline
                longest_segment = vs

        return longest_segment

    # ==========================================================================

    def get_highest_polyline(self):

        highest_polyline = list()
        z_max = float("-inf")
        for vs in self.voxel_segments:
            z = numpy.max(numpy.array(vs.polyline)[:, 2])

            if z > z_max:
                z_max = z
                highest_polyline = vs

        return highest_polyline

    def get_real_index_position_base(self):

        voxels_position = self.voxels_position()
        long_polyline = self.get_longest_segment().polyline
        index_position_base = len(long_polyline) - 1
        for i in range(len(long_polyline) - 1, -1, -1):
            if long_polyline[i] in set(voxels_position):
                index_position_base = i
            else:
                break
        return index_position_base

    def real_longest_polyline(self):

        long_polyline = self.get_longest_segment().polyline
        index_position_base = self.get_real_index_position_base()

        real_polyline = long_polyline[index_position_base:]

        return real_polyline
