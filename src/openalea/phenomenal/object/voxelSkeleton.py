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

from .voxelGrid import VoxelGrid
# ==============================================================================


class VoxelSkeleton(object):

    def __init__(self, voxels_size):
        self.voxel_segments = list()
        self.voxels_size = voxels_size

    def add_voxel_segment(self, voxel_segment):
        self.voxel_segments.append(voxel_segment)

    def voxels_position(self):
        voxels_position = set()
        for voxel_segment in self.voxel_segments:
            voxels_position = voxels_position.union(
                voxel_segment.voxels_position)
        return numpy.array(list(voxels_position))

    def voxels_position_polyline(self):
        voxels_position = set()
        for voxel_segment in self.voxel_segments:
            voxels_position = voxels_position.union(voxel_segment.polyline)
        return numpy.array(list(voxels_position))

    def volume(self):
        return len(self.voxels_position()) * self.voxels_size ** 3

    def to_voxel_grid(self):
        return VoxelGrid(self.voxels_position(), self.voxels_size)