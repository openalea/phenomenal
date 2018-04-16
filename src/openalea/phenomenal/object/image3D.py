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

import os
import numpy
import cv2
# ==============================================================================


class Image3D(numpy.ndarray):

    def __new__(cls,
                input_array,
                voxels_size=1,
                world_coordinate=(0, 0, 0),
                dtype=numpy.uint8,
                order='C'):

        if not isinstance(input_array, numpy.ndarray):
            raise TypeError('input_array must be a numpy.ndarray')

        if input_array.ndim != 3:
            raise ValueError("input_array must be numpy.ndarray of ndim == 3")

        obj = numpy.asarray(input_array, dtype=dtype, order=order).view(cls)
        obj.voxels_size = voxels_size
        obj.world_coordinate = world_coordinate

        return obj

    def __array_finalize__(self, obj):

        if obj is None:
            return

        self.voxels_size = getattr(obj, 'voxels_size', 1)
        self.world_coordinate = getattr(obj, 'world_coordinate', (0, 0, 0))

    # ==========================================================================
    # TRANSFORM
    # ==========================================================================

    # def to_VoxelPointCloud(self,
    #                        voxels_value=1,
    #                        voxels_size=None,
    #                        world_coordinate=None):
    #
    #     xx, yy, zz = numpy.where(self >= voxels_value)
    #
    #     if voxels_size is None:
    #         voxels_size = self.voxels_size
    #
    #     if world_coordinate is None:
    #         world_coordinate = self.world_coordinate
    #
    #     xxx = world_coordinate[0] + xx * voxels_size
    #     yyy = world_coordinate[1] + yy * voxels_size
    #     zzz = world_coordinate[2] + zz * voxels_size
    #
    #     voxels_position = zip(xxx, yyy, zzz)
    #
    #     return VoxelGrid(voxels_position, voxels_size)

    # ==========================================================================
    # READ / WRITE
    # ==========================================================================

    def write_to_npz(self, filename):

        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        numpy.savez_compressed(filename,
                               image=self,
                               voxels_size=self.voxels_size,
                               world_coordinate=self.world_coordinate,
                               allow_pickle=False)

    @staticmethod
    def read_from_npz(filename):
        npz = numpy.load(filename, allow_pickle=False)

        image = npz['image']
        voxels_size = int(npz['voxels_size'])
        world_coordinate = tuple(npz['world_coordinate'])

        return Image3D(image,
                       voxels_size=voxels_size,
                       world_coordinate=world_coordinate)

    def write_to_stack_image(self, folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        xl, yl, zl = self.shape
        for i in range(zl):
            mat = self[:, :, i] * 255
            cv2.imwrite(folder_name + '%d.png' % i, mat)

    # ==========================================================================
    # CREATION ROUTINE
    # ==========================================================================

    @staticmethod
    def zeros(shape,
              voxels_size=1,
              world_coordinate=(0, 0, 0),
              dtype=numpy.uint8,
              order='C'):

        if len(shape) != 3:
            raise ValueError("shape len must be equal to 3")

        return Image3D(numpy.zeros(shape),
                       voxels_size=voxels_size,
                       world_coordinate=world_coordinate,
                       dtype=dtype,
                       order=order)

    @staticmethod
    def zeros_like(image_3d):

        if not isinstance(image_3d, Image3D):
            raise TypeError("image_3d must be a Image3D type")

        if image_3d.flags['C_CONTIGUOUS']:
            order = 'C'
        else:
            order = 'F'

        return Image3D.zeros(image_3d.shape,
                             voxels_size=image_3d.voxels_size,
                             world_coordinate=image_3d.world_coordinate,
                             dtype=image_3d.dtype,
                             order=order)

    @staticmethod
    def ones(shape,
             voxels_size=1,
             world_coordinate=(0, 0, 0),
             dtype=numpy.uint8,
             order='C'):

        if len(shape) != 3:
            raise ValueError("shape len must be equal to 3")

        return Image3D(numpy.ones(shape),
                       voxels_size=voxels_size,
                       world_coordinate=world_coordinate,
                       dtype=dtype,
                       order=order)

    @staticmethod
    def ones_like(image_3d):

        if not isinstance(image_3d, Image3D):
            raise TypeError("image_3d must be a Image3D type")

        if image_3d.flags['C_CONTIGUOUS']:
            order = 'C'
        else:
            order = 'F'

        return Image3D.ones(image_3d.shape,
                            voxels_size=image_3d.voxels_size,
                            world_coordinate=image_3d.world_coordinate,
                            dtype=image_3d.dtype,
                            order=order)