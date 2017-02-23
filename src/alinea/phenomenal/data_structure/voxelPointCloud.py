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

from alinea.phenomenal.data_structure.image3d import Image3D
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

    # ==========================================================================
    # CONVERSION
    # ==========================================================================

    def to_image_3d(self):
            (x_min, y_min, z_min), (x_max, y_max, z_max) = self.bounding_box()

            len_x = int((x_max - x_min) / self.voxels_size + 1)
            len_y = int((y_max - y_min) / self.voxels_size + 1)
            len_z = int((z_max - z_min) / self.voxels_size + 1)

            image_3d = Image3D.zeros((len_x, len_y, len_z),
                                     dtype=numpy.bool,
                                     voxels_size=self.voxels_size,
                                     world_coordinate=(x_min, y_min, z_min))

            bound_min = numpy.array((x_min, y_min, z_min))
            vs_pos = numpy.array(self.voxels_position)

            r = ((vs_pos - bound_min) / self.voxels_size).astype(int)
            image_3d[r[:, 0], r[:, 1], r[:, 2]] = 1

            return image_3d

    @staticmethod
    def from_image_3d(image_3d,
                      voxels_value=1,
                      voxels_size=None,
                      world_coordinate=None):

        xx, yy, zz = numpy.where(image_3d >= voxels_value)

        if voxels_size is None:
            voxels_size = image_3d.voxels_size

        if world_coordinate is None:
            world_coordinate = image_3d.world_coordinate

        xxx = world_coordinate[0] + xx * voxels_size
        yyy = world_coordinate[1] + yy * voxels_size
        zzz = world_coordinate[2] + zz * voxels_size

        voxels_position = zip(xxx, yyy, zzz)

        return VoxelPointCloud(voxels_position, voxels_size)

    @staticmethod
    def from_numpy_image(image_3d, voxels_value, voxels_size, world_coordinate):

        xx, yy, zz = numpy.where(image_3d >= voxels_value)

        if voxels_size is None:
            voxels_size = image_3d.voxels_size

        if world_coordinate is None:
            world_coordinate = image_3d.world_coordinate

        xxx = world_coordinate[0] + xx * voxels_size
        yyy = world_coordinate[1] + yy * voxels_size
        zzz = world_coordinate[2] + zz * voxels_size

        voxels_position = zip(xxx, yyy, zzz)

        # voxels_position = list()
        # for i in range(len(xxx)):
        #     voxels_position.append((xxx[i], yyy[i], zzz[i]))

        return VoxelPointCloud(voxels_position, voxels_size)

    # ==========================================================================
    # READ / WRITE
    # ==========================================================================

    def write_to_npz(self, filename):
        image_3d = self.to_image_3d()
        image_3d.write_to_npz(filename)

    @staticmethod
    def read_from_npz(filename):
        image_3d = Image3D.read_from_npz(filename)
        return VoxelPointCloud.from_image_3d(image_3d)

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

    def write_to_xyz(self, filename):

        if (os.path.dirname(filename) and not os.path.exists(os.path.dirname(
                filename))):
            os.makedirs(os.path.dirname(filename))

        f = open(filename, 'wb')
        for x, y, z in self.voxels_position:
            f.write("%f %f %f \n" % (x, y, z))
        f.close()

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

    def write_to_csv(self, filename):

        if (os.path.dirname(filename) and not os.path.exists(os.path.dirname(
                filename))):
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'wb') as f:
            c = csv.writer(f)

            c.writerow(['x_coord', 'y_coord', 'z_coord', 'voxel_size'])

            for x, y, z in self.voxels_position:
                c.writerow([x, y, z, self.voxels_size])

    @staticmethod
    def read_from_csv(filename):
        with open(filename, 'rb') as f:
            reader = csv.reader(f)

            next(reader)
            x, y, z, vs = next(reader)

            voxels_size = float(vs)

            voxels_position = list()
            voxels_position.append((float(x), float(y), float(z)))

            for x, y, z, vs in reader:
                voxels_position.append((float(x), float(y), float(z)))

            return VoxelPointCloud(voxels_position, voxels_size)
