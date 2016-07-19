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
import numpy
# ==============================================================================


class Image3D(numpy.ndarray):

    def __new__(cls,
                input_array,
                voxel_size=1,
                world_coordinate=(0, 0, 0),
                dtype=numpy.uint8,
                order='C'):

        if not isinstance(input_array, numpy.ndarray):
            raise TypeError('input_array must be a numpy.ndarray')

        if input_array.ndim != 3:
            raise ValueError("input_array must be numpy.ndarray of ndim == 3")

        obj = numpy.asarray(input_array, dtype=dtype, order=order).view(cls)
        obj.voxel_size = voxel_size
        obj.world_coordinate = world_coordinate

        return obj

    def __array_finalize__(self, obj):

        if obj is None:
            return

        self.voxel_size = getattr(obj, 'voxel_size', 1)
        self.world_coordinate = getattr(obj, 'world_coordinate', (0, 0, 0))

    @staticmethod
    def zeros(shape,
              voxel_size=1,
              world_coordinate=(0, 0, 0),
              dtype=numpy.uint8,
              order='C'):

        if len(shape) != 3:
            raise ValueError("shape len must be equal to 3")

        return Image3D(numpy.zeros(shape),
                       voxel_size=voxel_size,
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
                             voxel_size=image_3d.voxel_size,
                             world_coordinate=image_3d.world_coordinate,
                             dtype=image_3d.dtype,
                             order=order)

    @staticmethod
    def ones(shape,
             voxel_size=1,
             world_coordinate=(0, 0, 0),
             dtype=numpy.uint8,
             order='C'):

        if len(shape) != 3:
            raise ValueError("shape len must be equal to 3")

        return Image3D(numpy.ones(shape),
                       voxel_size=voxel_size,
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
                            voxel_size=image_3d.voxel_size,
                            world_coordinate=image_3d.world_coordinate,
                            dtype=image_3d.dtype,
                            order=order)

