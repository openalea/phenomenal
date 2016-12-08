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

# ==============================================================================


class VoxelSegment(object):

    def __init__(self, voxels_center, voxels_size, paths, label):
        self.voxels_center = voxels_center
        self.voxels_size = voxels_size
        self.paths = paths
        self.label = label


class VoxelPointCloudSegments(object):

    def __init__(self):
        self.voxel_point_cloud_segment = list()

    def add_voxel_segment(self, voxels_center, voxels_size, paths, label):
        voxel_segment = VoxelSegment(voxels_center, voxels_size, paths, label)
        self.voxel_point_cloud_segment.append(voxel_segment)

    def write_to_json(self, filename):
        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'w') as f:

            data = list()
            for v in self.voxel_point_cloud_segment:
                d = v.__dict__.copy()
                d['voxels_center'] = list(d['voxels_center'])
                data.append(d)

            json.dump(data, f)

    @staticmethod
    def read_from_json(filename):

        with open(filename, 'rb') as f:
            data = json.load(f)

            vpcs = VoxelPointCloudSegments()

            for d in data:
                voxels_center = set(map(tuple, d['voxels_center']))

                paths = list()
                for path in d["paths"]:
                    paths.append(map(tuple, path))

                vpcs.add_voxel_segment(
                    voxels_center, d['voxels_size'], paths, d['label'])

        return vpcs

