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
import os
import gzip
import json

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



    def write_to_json_gz(self, filename):

        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        with gzip.open(filename, 'wb') as f:

            data = dict()
            data['segments'] = list()
            data['voxels_size'] = self.voxels_size

            for seg in self.segments:

                dseg = dict()
                dseg['closest_nodes'] = seg.closest_nodes
                dseg['voxels_position'] = seg.voxels_position
                dseg['polyline'] = seg.polyline

                data['segments'].append(dseg)

            f.write(json.dumps(data).encode('utf-8'))

