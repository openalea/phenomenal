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
import re
import json
# ==============================================================================


class VoxelPointCloud(object):

    def __init__(self, voxels_center, voxels_size):

        self.voxels_center = voxels_center
        self.voxels_size = voxels_size

    def bounding_box(self):

        if not self.voxels_center:
            raise ValueError("Empty list")

        x_min = float("inf")
        y_min = float("inf")
        z_min = float("inf")

        x_max = - float("inf")
        y_max = - float("inf")
        z_max = - float("inf")

        for x, y, z in self.voxels_center:
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            z_min = min(z_min, z)

            x_max = max(x_max, x)
            y_max = max(y_max, y)
            z_max = max(z_max, z)

        return (x_min, y_min, z_min), (x_max, y_max, z_max)

    def volume(self):
        """
        Compute the volume of the voxel point cloud

        Returns
        -------
        out : int
            Error value
        """

        return len(self.voxels_center) * self.voxels_size ** 3

    def write_to_json(self, filename):

        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'w') as f:

            data = dict()
            data['voxels_size'] = self.voxels_size
            data['voxels_center'] = list(self.voxels_center)

            json.dump(data, f)

    @staticmethod
    def read_from_json(filename):

        with open(filename, 'rb') as f:
            data = json.load(f)
            voxels_size = data['voxels_size']
            voxels_center = data['voxels_center']
            voxels_center = map(tuple, voxels_center)

            return VoxelPointCloud(voxels_center, voxels_size)

    @staticmethod
    def read_from_xyz(filename, voxels_size):

        voxels_center = list()
        with open(filename, 'r') as f:
            for line in f:
                point_3d = re.findall(r'[-0-9.]+', line)

                x = float(point_3d[0])
                y = float(point_3d[1])
                z = float(point_3d[2])

                voxels_center.append((x, y, z))
        f.close()

        return VoxelPointCloud(voxels_center, voxels_size)
