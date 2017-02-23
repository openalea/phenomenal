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
import numpy

from alinea.phenomenal.data_structure import (
    VoxelSegment,
    VoxelPointCloud)
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

    # ==========================================================================
    # READ / WRITE
    # ==========================================================================

    def write_to_npz(self, filename):

        number_voxel_segments = len(self.voxel_segments)
        if number_voxel_segments == 0:
            raise ValueError('Nothing to write')

        voxels_size = self.voxel_segments[0].voxels_size

        all_voxels = set()
        for voxel_segment in self.voxel_segments:
            all_voxels = all_voxels.union(set(voxel_segment.voxels_position))
        all_voxels = list(all_voxels)

        # ======================================================================

        vpc = VoxelPointCloud(all_voxels, voxels_size)
        (x_min, y_min, z_min), (x_max, y_max, z_max) = vpc.bounding_box()

        len_x = int((x_max - x_min) / voxels_size + 1)
        len_y = int((y_max - y_min) / voxels_size + 1)
        len_z = int((z_max - z_min) / voxels_size + 1)

        world_coordinate = (x_min, y_min, z_min)
        voxels_image = numpy.zeros((len_x, len_y, len_z, 2), dtype=numpy.int64)
        poly_image = numpy.zeros((len_x, len_y, len_z, 2), dtype=numpy.int64)

        for i, voxel_segment in enumerate(self.voxel_segments):

            value = 1 << i

            for x, y, z in voxel_segment.voxels_position:
                x_new = int((x - x_min) / voxels_size)
                y_new = int((y - y_min) / voxels_size)
                z_new = int((z - z_min) / voxels_size)

                voxels_image[x_new, y_new, z_new] |= value

            for x, y, z in voxel_segment.polylines[0]:
                x_new = int((x - x_min) / voxels_size)
                y_new = int((y - y_min) / voxels_size)
                z_new = int((z - z_min) / voxels_size)

                poly_image[x_new, y_new, z_new] |= value

        # ======================================================================

        numpy.savez_compressed(filename,
                               voxels_image=voxels_image,
                               poly_image=poly_image,
                               voxels_size=voxels_size,
                               world_coordinate=world_coordinate,
                               number_voxel_segments=number_voxel_segments,
                               allow_pickle=False)

    @staticmethod
    def read_from_npz(filename):
        npz = numpy.load(filename, allow_pickle=False)

        voxels_image = npz['voxels_image']
        poly_image = npz['poly_image']
        voxels_size = int(npz['voxels_size'])
        world_coordinate = tuple(npz['world_coordinate'])
        number_voxel_segments = int(npz['number_voxel_segments'])

        voxel_segments = list()
        for i in range(number_voxel_segments):
            value = i << i
            voxels_im = numpy.bitwise_and(voxels_image, value)
            voxels_vpc = VoxelPointCloud.from_numpy_image(
                voxels_im, value, voxels_size, world_coordinate)

            poly_im = numpy.bitwise_and(poly_image, value)
            poly_vpc = VoxelPointCloud.from_numpy_image(
                poly_im, value, voxels_size, world_coordinate)

            vs = VoxelSegment(voxels_vpc.voxels_position,
                              voxels_vpc.voxels_size,
                              poly_vpc.voxels_position)

            voxel_segments.append(vs)

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
