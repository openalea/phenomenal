# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import os
import numpy
import cv2
import vtk
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy

# ==============================================================================


class Image3D(numpy.ndarray):
    def __new__(
        cls,
        input_array,
        voxels_size=1,
        world_coordinate=(0, 0, 0),
        dtype=numpy.uint8,
        order="C",
    ):
        if not isinstance(input_array, numpy.ndarray):
            raise TypeError("input_array must be a numpy.ndarray")

        if input_array.ndim != 3:
            raise ValueError("input_array must be numpy.ndarray of ndim == 3")

        obj = numpy.asarray(input_array, dtype=dtype, order=order).view(cls)
        obj.voxels_size = voxels_size
        obj.world_coordinate = world_coordinate

        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return

        self.voxels_size = getattr(obj, "voxels_size", 1)
        self.world_coordinate = getattr(obj, "world_coordinate", (0, 0, 0))

    # ==========================================================================
    # TRANSFORM
    # ==========================================================================

    @property
    def vtk_image_data(self):
        """Return a vtkImageData representation of this image."""
        image = vtk.vtkImageData()

        nx, ny, nz = self.shape
        image.SetDimensions(nx, ny, nz)

        if numpy.isscalar(self.voxels_size):
            spacing = (self.voxels_size,) * 3
        else:
            spacing = self.voxels_size

        image.SetSpacing(*spacing)
        image.SetOrigin(*self.world_coordinate)

        vtk_array = numpy_to_vtk(
            numpy.ascontiguousarray(self.astype(numpy.uint8)).ravel(order="F"),
            deep=True,
        )
        vtk_array.SetNumberOfComponents(1)

        image.GetPointData().SetScalars(vtk_array)

        return image
    @staticmethod
    def from_vtk_image(vtk_image):
        """Create an Image3D from vtkImageData."""
        dimensions = vtk_image.GetDimensions()

        vtk_array = vtk_image.GetPointData().GetScalars()
        if vtk_array is None:
            raise ValueError("vtkImageData has no point scalars")

        if vtk_array.GetNumberOfComponents() != 1:
            raise ValueError("Expected a single-component scalar image")

        array = vtk_to_numpy(vtk_array).reshape(dimensions, order="F")

        return Image3D(
            array,
            voxels_size=vtk_image.GetSpacing(),
            world_coordinate=vtk_image.GetOrigin(),
            dtype=array.dtype,
            order="F",
        )

    @staticmethod
    def from_voxel_grid(voxel_grid):
        voxels_position = numpy.asarray(voxel_grid.voxels_position)
        voxels_size = voxel_grid.voxels_size

        if voxels_position.size == 0:
            return Image3D(
                numpy.zeros((0, 0, 0), dtype=numpy.uint8),
                voxels_size=voxels_size,
                world_coordinate=(0, 0, 0),
            )

        world_coordinate = voxels_position.min(axis=0)

        indices = numpy.rint(
            (voxels_position - world_coordinate) / voxels_size
        ).astype(int)

        shape = indices.max(axis=0) + 1
        image = numpy.zeros(shape, dtype=numpy.uint8)
        image[tuple(indices.T)] = 1

        return Image3D(
            image,
            voxels_size=voxels_size,
            world_coordinate=world_coordinate,
        )
    # ==========================================================================
    # READ / WRITE
    # ==========================================================================

    def write_to_npz(self, filename):
        if os.path.dirname(filename) and not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        numpy.savez_compressed(
            filename,
            image=self,
            voxels_size=self.voxels_size,
            world_coordinate=self.world_coordinate,
            allow_pickle=False,
        )

    @staticmethod
    def read_from_npz(filename):
        npz = numpy.load(filename, allow_pickle=False)

        image = npz["image"]
        voxels_size = int(npz["voxels_size"])
        world_coordinate = tuple(npz["world_coordinate"])

        return Image3D(
            image, voxels_size=voxels_size, world_coordinate=world_coordinate
        )

    def write_to_stack_image(self, folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        _, _, zl = self.shape
        for i in range(zl):
            mat = self[:, :, i] * 255
            cv2.imwrite(folder_name + f"{i}.png", mat)

    # ==========================================================================
    # CREATION ROUTINE
    # ==========================================================================

    @staticmethod
    def zeros(
        shape, voxels_size=1, world_coordinate=(0, 0, 0), dtype=numpy.uint8, order="C"
    ):
        if len(shape) != 3:
            raise ValueError("shape len must be equal to 3")

        return Image3D(
            numpy.zeros(shape),
            voxels_size=voxels_size,
            world_coordinate=world_coordinate,
            dtype=dtype,
            order=order,
        )

    @staticmethod
    def zeros_like(image_3d):
        if not isinstance(image_3d, Image3D):
            raise TypeError("image_3d must be a Image3D type")

        if image_3d.flags["C_CONTIGUOUS"]:
            order = "C"
        else:
            order = "F"

        return Image3D.zeros(
            image_3d.shape,
            voxels_size=image_3d.voxels_size,
            world_coordinate=image_3d.world_coordinate,
            dtype=image_3d.dtype,
            order=order,
        )

    @staticmethod
    def ones(
        shape, voxels_size=1, world_coordinate=(0, 0, 0), dtype=numpy.uint8, order="C"
    ):
        if len(shape) != 3:
            raise ValueError("shape len must be equal to 3")

        return Image3D(
            numpy.ones(shape),
            voxels_size=voxels_size,
            world_coordinate=world_coordinate,
            dtype=dtype,
            order=order,
        )

    @staticmethod
    def ones_like(image_3d):
        if not isinstance(image_3d, Image3D):
            raise TypeError("image_3d must be a Image3D type")

        if image_3d.flags["C_CONTIGUOUS"]:
            order = "C"
        else:
            order = "F"

        return Image3D.ones(
            image_3d.shape,
            voxels_size=image_3d.voxels_size,
            world_coordinate=image_3d.world_coordinate,
            dtype=image_3d.dtype,
            order=order,
        )
