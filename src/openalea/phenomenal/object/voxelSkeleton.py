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

    def __init__(self, segments, voxels_size):
        self.segments = segments
        self.voxels_size = voxels_size

    def voxels_position(self):
        voxels_position = set()
        for segment in self.segments:
            voxels_position = voxels_position.union(
                segment.voxels_position)
        return numpy.array(list(voxels_position))

    def voxels_position_polyline(self):
        voxels_position = set()
        for segment in self.segments:
            voxels_position = voxels_position.union(segment.polyline)
        return numpy.array(list(voxels_position))

    def volume(self):
        return len(self.voxels_position()) * self.voxels_size ** 3

    def to_voxel_grid(self):
        return VoxelGrid(self.voxels_position(), self.voxels_size)
