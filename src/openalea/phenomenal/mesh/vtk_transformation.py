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

import operator
import vtk
import vtkmodules.util.numpy_support

# ==============================================================================

__all__ = [
    "from_vertices_faces_to_vtk_poly_data",
    "from_vtk_poly_data_to_vertices_faces",
    "from_voxel_centers_to_vtk_image_data",
    "from_numpy_matrix_to_vtk_image_data",
    "from_vtk_image_data_to_voxels_center",
    "voxel_grid_to_vtk_poly_data",
]

# ==============================================================================


def voxel_grid_to_vtk_poly_data(voxel_grid):
    """
    Get a vtkPolyData object from VoxelGrid object.

    Parameters
    -----------
    voxel_grid: VoxelGrid
        The voxel grid to transform.

    Returns
    -------
    poly_data: vtk.vtkPolyData
        A vtkPolyData object
    """
    voxels_position = voxel_grid.voxels_position
    voxels_size = voxel_grid.voxels_size

    points = vtk.vtkPoints()
    for v in voxels_position:
        points.InsertNextPoint(v[0], v[1], v[2])

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    cube_source = vtk.vtkCubeSource()
    cube_source.SetXLength(voxels_size)
    cube_source.SetYLength(voxels_size)
    cube_source.SetZLength(voxels_size)

    glyph3_d = vtk.vtkGlyph3D()

    if vtk.VTK_MAJOR_VERSION <= 5:
        glyph3_d.SetSource(cube_source.GetOutput())
        glyph3_d.SetInput(polydata)
    else:
        glyph3_d.SetSourceConnection(cube_source.GetOutputPort())
        glyph3_d.SetInputData(polydata)

    glyph3_d.Update()

    return glyph3_d.GetOutput()


def from_vertices_faces_to_vtk_poly_data(
    vertices, faces, vertices_colors=None, faces_colors=None
):
    """
    Get a vtkPolyData object from lists of vertices and faces.

    Parameters
    ----------
    vertices: list[tuple]
        A list of tuple of vertex positions.
    faces: list[tuple]
        A list of tuple of faces id.
    vertices_colors: list[tuple]
        A list of RGB color tuple per vertices.
    faces_colors: list[tuple]
        A list of RGB color tuple per faces.

    Returns
    -------
    poly_data: vtk.vtkPolyData
        A vtkPolyData object.
    """
    def make_vtk_id_list(it):
        vil = vtk.vtkIdList()
        for j in it:
            vil.InsertNextId(int(j))
        return vil

    poly_data = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    polys = vtk.vtkCellArray()

    # Load the point, cell, and data attributes.
    for i, vertex in enumerate(vertices):
        points.InsertPoint(i, vertex)
    for _, face in enumerate(faces):
        polys.InsertNextCell(make_vtk_id_list(face))

    # We now assign the pieces to the vtkPolyData.
    poly_data.SetPoints(points)
    del points
    poly_data.SetPolys(polys)
    del polys

    if vertices_colors is not None:
        vtk_colors = vtk.vtkUnsignedCharArray()
        vtk_colors.SetNumberOfComponents(3)
        vtk_colors.SetName("Colors")
        for color in vertices_colors:
            vtk_colors.InsertNextTuple3(color[0], color[1], color[2])
        poly_data.GetPointData().SetScalars(vtk_colors)

    if faces_colors is not None:
        vtk_colors = vtk.vtkUnsignedCharArray()
        vtk_colors.SetNumberOfComponents(3)
        vtk_colors.SetName("Colors")
        for color in faces_colors:
            vtk_colors.InsertNextTuple3(color[0], color[1], color[2])
        poly_data.GetCellData().SetScalars(vtk_colors)

    return poly_data


def from_vtk_poly_data_to_vertices_faces(vtk_poly_data):
    """
    Get vertices and faces from a vtkPolyData object

    Parameters
    ----------
    vtk_poly_data: vtk.vtkPolyData
        The vtkPolyData object to get info from

    Returns
    -------
    mesh: tuple
        A tuple containing vertices, faces and colors of the mesh
    """
    vertices = vtkmodules.util.numpy_support.vtk_to_numpy(
        vtk_poly_data.GetPoints().GetData()
    )

    faces = vtkmodules.util.numpy_support.vtk_to_numpy(
        vtk_poly_data.GetPolys().GetData()
    )

    faces = faces.reshape((len(faces) // 4, 4))

    colors = vtk_poly_data.GetPointData().GetScalars()

    return vertices, faces[:, 1:], colors


def from_numpy_matrix_to_vtk_image_data(data_matrix):
    """
    Get a vtkImageData from a matrix.

    Parameters
    ----------
    data_matrix: numpy.matrix
        The data matrix to get image info from.

    Returns
    -------
    image_data: vtk.vtkImageData
        A vtkImageData object with the matrix info.
    """
    nx, ny, nz = data_matrix.shape

    image_data = vtk.vtkImageData()
    image_data.SetDimensions(nx, ny, nz)
    image_data.SetSpacing(1.0, 1.0, 1.0)

    if vtk.VTK_MAJOR_VERSION < 6:
        image_data.SetScalarType(
            vtkmodules.util.numpy_support.get_vtk_array_type(data_matrix.dtype)
        )
        image_data.SetNumberOfScalarComponents(1)
        image_data.AllocateScalars()
    else:
        image_data.AllocateScalars(
            vtkmodules.util.numpy_support.get_vtk_array_type(data_matrix.dtype), 1
        )

    lx, ly, lz = image_data.GetDimensions()

    for i in range(lx):
        for j in range(ly):
            for k in range(lz):
                image_data.SetScalarComponentFromDouble(
                    i, j, k, 0, data_matrix[i, j, k]
                )

    return image_data


def from_vtk_image_data_to_voxels_center(image_data, true_value=255, component=0):
    """
    Get voxels center from a vtkImageData object.

    Parameters
    ----------
    image_data: vtk.vtkImageData
        The vtkImageData object.
    true_value: int
    component: int

    Returns
    -------
    voxels_points: list
        A list of voxel positions.
    """
    dim_x, dim_y, dim_z = image_data.GetDimensions()
    ori_x, ori_y, ori_z = image_data.GetOrigin()
    spa_x, spa_y, spa_z = image_data.GetSpacing()

    voxels_points = []
    for x in range(dim_x):
        for y in range(dim_y):
            for z in range(dim_z):
                r = image_data.GetScalarComponentAsDouble(x, y, z, component)

                if r == true_value:
                    voxels_points.append(
                        (x * spa_x + ori_x, y * spa_y + ori_y, z * spa_z + ori_z)
                    )

    return voxels_points


def from_voxel_centers_to_vtk_image_data(voxel_centers, voxel_size):
    """
    Get a vtkImageData object from a list of voxel centers.

    Parameters
    ----------
    voxel_centers: list[tuple]
        A list of voxel centers.
    voxel_size: int
        The size each voxel.

    Returns
    -------
    image_data: tuple
        A tuple containing the vtkImageData object and the min voxel position
        values.

    """
    x_min = min(voxel_centers, key=operator.itemgetter(0))[0]
    x_max = max(voxel_centers, key=operator.itemgetter(0))[0]

    y_min = min(voxel_centers, key=operator.itemgetter(1))[1]
    y_max = max(voxel_centers, key=operator.itemgetter(1))[1]

    z_min = min(voxel_centers, key=operator.itemgetter(2))[2]
    z_max = max(voxel_centers, key=operator.itemgetter(2))[2]

    nx, ny, nz = (
        int((x_max - x_min) / voxel_size + 1),
        int((y_max - y_min) / voxel_size + 1),
        int((z_max - z_min) / voxel_size + 1),
    )

    image_data = vtk.vtkImageData()
    image_data.SetDimensions(nx, ny, nz)
    image_data.SetSpacing(1.0, 1.0, 1.0)

    if vtk.VTK_MAJOR_VERSION < 6:
        image_data.SetScalarType(vtk.VTK_UNSIGNED_CHAR)
        image_data.SetNumberOfScalarComponents(1)
        image_data.AllocateScalars()
    else:
        image_data.AllocateScalars(vtk.VTK_DOUBLE, 0)

    # Wrong initialization, image_data not initialize to 0 value
    for x, y, z in voxel_centers:
        nx = int((x - x_min) / voxel_size)
        ny = int((y - y_min) / voxel_size)
        nz = int((z - z_min) / voxel_size)

        image_data.SetScalarComponentFromDouble(nx, ny, nz, 0, 1)

    return image_data, (x_min, y_min, z_min)
