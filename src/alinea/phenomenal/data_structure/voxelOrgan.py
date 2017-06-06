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
from alinea.phenomenal.data_structure import (
    VoxelSegment)
# ==============================================================================


class VoxelOrgan(object):

    def __init__(self, label):
        self.voxel_segments = list()
        self.label = label
        self.info = dict()

    def add_voxel_segment(self, voxels_position, polyline):
        self.voxel_segments.append(VoxelSegment(voxels_position, polyline))

    def voxels_position(self):

        voxels_position = set()
        for voxel_segment in self.voxel_segments:
            voxels_position = voxels_position.union(
                voxel_segment.voxels_position)

        return voxels_position
