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

# ==============================================================================


class VoxelSegment(object):

    def __init__(self, polyline, closest_nodes):

        self.polyline = polyline
        self.closest_nodes = closest_nodes
        self.voxels_position = set().union(*self.closest_nodes)

    def __len__(self):
        return len(self.voxels_position)


