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


class VoxelSkeleton(object):

    def __init__(self, voxels_size):
        self.voxel_segments = list()
        self.voxels_size = voxels_size

    def add_voxel_segment(self, voxel_segment):
        self.voxel_segments.append(voxel_segment)
