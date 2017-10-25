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

from openalea.phenomenal.object import (
    VoxelSegment,
    VoxelGrid)
# ==============================================================================


class VoxelSkeleton(object):

    def __init__(self, voxels_size, ball_radius):
        self.voxel_segments = list()
        self.voxels_size = voxels_size
        self.ball_radius = ball_radius

    def add_voxel_segment(self, voxels_position, polyline):
        self.voxel_segments.append(VoxelSegment(voxels_position, polyline))

    def get_leaf_order(self, number):
        for vs in self.voxel_segments:
            if "order" in vs.info and vs.info["order"] == number:
                return vs

    def swap_leaf_order(self, number_1, number_2):
        vs1 = self.get_leaf_order(number_1)
        vs2 = self.get_leaf_order(number_2)

        vs1.info['order'] = number_2
        vs2.info['order'] = number_1

    def get_stem(self):
        for vs in self.voxel_segments:
            if vs.label == "stem":
                return vs
        return None

    def get_unknown(self):
        for vs in self.voxel_segments:
            if vs.label == "unknown":
                return vs

    def get_mature_leafs(self):
        mature_leafs = list()
        for vs in self.voxel_segments:
            if vs.label == "mature_leaf":
                mature_leafs.append(vs)
        return mature_leafs

    def get_cornet_leafs(self):
        cornet_leafs = list()
        for vs in self.voxel_segments:
            if vs.label == "cornet_leaf":
                cornet_leafs.append(vs)
        return cornet_leafs

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

        vpc = VoxelGrid(all_voxels, voxels_size)
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
            voxels_vpc = VoxelGrid.from_numpy_image(
                voxels_im, value, voxels_size, world_coordinate)

            poly_im = numpy.bitwise_and(poly_image, value)
            poly_vpc = VoxelGrid.from_numpy_image(
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

            data = dict()
            data['voxels_size'] = self.voxels_size
            data['ball_radius'] = self.ball_radius

            data['voxel_segments'] = list()
            for v in self.voxel_segments:
                d = dict()
                d['polyline'] = v.polyline
                d['voxels_position'] = list(v.voxels_position)
                data['voxel_segments'].append(d)

            json.dump(data, f)

    @staticmethod
    def read_from_json(filename):

        with open(filename, 'rb') as f:
            data = json.load(f)

            voxel_skeleton = VoxelSkeleton(data['voxels_size'],
                                           data['ball_radius'])

            for d in data['voxel_segments']:
                voxels_position = set(map(tuple, d['voxels_position']))
                polyline = map(tuple, list(d["polyline"]))
                voxel_skeleton.add_voxel_segment(
                    voxels_position, polyline)

        return voxel_skeleton
