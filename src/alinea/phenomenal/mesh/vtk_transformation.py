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
import vtk

from vtk.util.numpy_support import get_vtk_array_type
from operator import itemgetter
# ==============================================================================


def from_vertices_faces_to_vtk_poly_data(vertices, faces):
    # Makes a vtkIdList from a Python iterable. I'm kinda surprised that
    # this is necessary, since I assumed that this kind of thing would
    # have been built into the wrapper and happen transparently, but it
    # seems not.
    def make_vtk_id_list(it):
        vil = vtk.vtkIdList()
        for j in it:
            vil.InsertNextId(int(j))
        return vil

    poly_data = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    polys = vtk.vtkCellArray()

    # Load the point, cell, and data attributes.
    for i in range(len(vertices)):
        points.InsertPoint(i, vertices[i])
    for i in range(len(faces)):
        polys.InsertNextCell(make_vtk_id_list(faces[i]))

    # We now assign the pieces to the vtkPolyData.
    poly_data.SetPoints(points)
    del points
    poly_data.SetPolys(polys)
    del polys

    return poly_data


def from_vtk_poly_data_to_vertices_faces(vtk_poly_data):
    vertices = vtk.util.numpy_support.vtk_to_numpy(
        vtk_poly_data.GetPoints().GetData())

    faces = vtk.util.numpy_support.vtk_to_numpy(
        vtk_poly_data.GetPolys().GetData())

    faces = faces.reshape((len(faces) / 4, 4))

    return vertices, faces[:, 1:]


def from_voxel_centers_to_vtk_image_data(voxel_centers, voxel_size):

    x_min = min(voxel_centers, key=itemgetter(0))[0]
    x_max = max(voxel_centers, key=itemgetter(0))[0]

    y_min = min(voxel_centers, key=itemgetter(1))[1]
    y_max = max(voxel_centers, key=itemgetter(1))[1]

    z_min = min(voxel_centers, key=itemgetter(2))[2]
    z_max = max(voxel_centers, key=itemgetter(2))[2]

    image_data = vtk.vtkImageData()

    nx, ny, nz = (int((x_max - x_min) / voxel_size + 1),
                  int((y_max - y_min) / voxel_size + 1),
                  int((z_max - z_min) / voxel_size + 1))

    image_data.SetDimensions(nx, ny, nz)
    image_data.SetSpacing(1.0, 1.0, 1.0)

    print nx, ny, nz

    if vtk.VTK_MAJOR_VERSION < 6:
        image_data.SetScalarType(vtk.VTK_UNSIGNED_CHAR)
        image_data.SetNumberOfScalarComponents(1)
        image_data.AllocateScalars()
    else:
        image_data.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    # Wrong initialization, image_data not initialize to 0 value
    for x, y, z in voxel_centers:
        nx = int((x - x_min) / voxel_size)
        ny = int((y - y_min) / voxel_size)
        nz = int((z - z_min) / voxel_size)

        image_data.SetScalarComponentFromDouble(
            nx, ny, nz, 0, 1)

    return image_data, (x_min, y_min, z_min)


def from_numpy_matrix_to_vtk_image_data(data_matrix):
    nx, ny, nz = data_matrix.shape

    image_data = vtk.vtkImageData()
    image_data.SetDimensions(nx, ny, nz)
    image_data.SetSpacing(1.0, 1.0, 1.0)

    if vtk.VTK_MAJOR_VERSION < 6:
        image_data.SetScalarType(get_vtk_array_type(data_matrix.dtype))
        image_data.SetNumberOfScalarComponents(1)
        image_data.AllocateScalars()
    else:
        image_data.AllocateScalars(get_vtk_array_type(data_matrix.dtype), 1)

    lx, ly, lz = image_data.GetDimensions()

    for i in xrange(0, lx):
        for j in xrange(0, ly):
            for k in xrange(0, lz):
                image_data.SetScalarComponentFromDouble(
                    i, j, k, 0, data_matrix[i, j, k])

    return image_data
