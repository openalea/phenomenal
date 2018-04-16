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

# ==============================================================================


class VoxelSegment(object):

    def __init__(self, polyline, voxels_position, closest_nodes):

        self.polyline = polyline
        self.voxels_position = voxels_position
        self.closest_nodes = closest_nodes

    def __copy__(self):
        return type(self)(self.polyline,
                          self.voxels_position,
                          self.closest_nodes)

    def __len__(self):
        return len(self.voxels_position)
