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
import numpy
import csv
from ast import literal_eval

from alinea.phenomenal.data_structure.image3d import Image3D
from alinea.phenomenal.data_structure.voxelGraph import VoxelGraph
# ==============================================================================


class VoxelPointCloud(object):

    def __init__(self, voxels_position, voxels_size):

        self.voxels_position = voxels_position
        self.voxels_size = voxels_size

    def bounding_box(self):

        if not self.voxels_position:
            raise ValueError("Empty list")

        x_min = float("inf")
        y_min = float("inf")
        z_min = float("inf")

        x_max = - float("inf")
        y_max = - float("inf")
        z_max = - float("inf")

        for x, y, z in self.voxels_position:
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
        """

        return len(self.voxels_position) * self.voxels_size ** 3

    def to_image_3d(self):
            (x_min, y_min, z_min), (x_max, y_max, z_max) = self.bounding_box()

            len_x = int((x_max - x_min) / self.voxels_size + 1)
            len_y = int((y_max - y_min) / self.voxels_size + 1)
            len_z = int((z_max - z_min) / self.voxels_size + 1)

            image_3d = Image3D.zeros((len_x, len_y, len_z),
                                     dtype=numpy.bool,
                                     voxels_size=self.voxels_size,
                                     world_coordinate=(x_min, y_min, z_min))

            for x, y, z in self.voxels_position:
                x_new = int((x - x_min) / self.voxels_size)
                y_new = int((y - y_min) / self.voxels_size)
                z_new = int((z - z_min) / self.voxels_size)

                image_3d[x_new, y_new, z_new] = 1

            return image_3d

    def write_to_json(self, filename):

        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'w') as f:

            data = dict()
            data['voxels_size'] = self.voxels_size
            data['voxels_position'] = list(self.voxels_position)
            json.dump(data, f)

    @staticmethod
    def read_from_json(filename):

        with open(filename, 'rb') as f:
            data = json.load(f)
            voxels_size = data['voxels_size']
            voxels_position = data['voxels_position']
            voxels_position = map(tuple, voxels_position)

            return VoxelPointCloud(voxels_position, voxels_size)

    @staticmethod
    def read_from_xyz(filename, voxels_size):

        voxels_position = list()
        with open(filename, 'r') as f:
            for line in f:
                point_3d = re.findall(r'[-0-9.]+', line)

                x = float(point_3d[0])
                y = float(point_3d[1])
                z = float(point_3d[2])

                voxels_position.append((x, y, z))
        f.close()

        return VoxelPointCloud(voxels_position, voxels_size)

    @staticmethod
    def read_from_csv(filename):

        with open(filename, 'rb') as f:
            reader = csv.reader(f)

            next(reader)

            voxels_position = list()
            for number_id, position, size in reader:
                position = literal_eval(position)
                voxels_position.append(position)

            voxels_size

            return VoxelPointCloud(voxels_position, voxels_size)