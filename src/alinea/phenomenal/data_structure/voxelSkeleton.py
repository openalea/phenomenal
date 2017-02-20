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
import os
import json


from alinea.phenomenal.data_structure.voxelSegment import VoxelSegment
# ==============================================================================


class VoxelSkeleton(object):

    def __init__(self, voxel_segments=None):
        if voxel_segments is None:
            self.voxel_segments = list()
        else:
            self.voxel_segments = voxel_segments

    def add_voxel_segment(self, voxels_position, voxels_size, polylines, label):

        voxel_segment = VoxelSegment(voxels_position,
                                     voxels_size,
                                     polylines,
                                     label=label)

        self.voxel_segments.append(voxel_segment)

    def write_to_json(self, filename):
        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'w') as f:

            data = list()
            for v in self.voxel_segments:
                d = v.__dict__.copy()
                d['voxels_position'] = list(d['voxels_position'])

                data.append(d)

            json.dump(data, f)

    @staticmethod
    def read_from_json(filename):

        with open(filename, 'rb') as f:
            data = json.load(f)

            vpcs = VoxelSkeleton()

            for d in data:
                voxels_position = set(map(tuple, d['voxels_position']))

                polylines = list()
                for path in d["polylines"]:
                    polylines.append(map(tuple, path))

                vpcs.add_voxel_segment(
                    voxels_position, d['voxels_size'], polylines, d['label'])

        return vpcs
