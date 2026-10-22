# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import operator
import vtk
import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy, get_vtk_array_type
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData


# ==============================================================================

__all__ = [
    "from_mesh_to_vtk_poly_data",
    "from_vtk_poly_data_to_mesh",
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


def from_mesh_to_vtk_poly_data(vertices, faces, vertex_colors=None, face_colors=None, vertex_ids=None, face_ids=None):
    """Create a vtkPolyData mesh from vertices, triangular faces, and colors.

    Parameters
    ----------
    vertices : array-like, shape (N, 3)
        Vertex coordinates. Accepts a NumPy array or a sequence of
        three-dimensional coordinate sequences.

    faces : array-like, shape (M, 3)
        Triangle connectivity. Each row contains three indices into
        `vertices`. Accepts a NumPy array or a sequence of index sequences.

    vertex_colors : array-like, shape (N, 3), optional
        RGB color values for each vertex, with integer components in
        the range [0, 255].

    face_colors : array-like, shape (M, 3), optional
        RGB color values for each triangle, with integer components in
        the range [0, 255].

    Returns
    -------
    vtk.vtkPolyData
        A polygonal mesh containing the vertices, triangular faces,
        and optional point and cell RGB colors.
    """

    vertices = np.ascontiguousarray(vertices, dtype=np.float64)
    faces = np.asarray(faces, dtype=np.int64)
    if vertex_colors is not None and face_colors is not None:
        raise ValueError(
            "Specify either vertices_colors or faces_colors, not both"
        )
    if vertex_colors is not None:
        colors = np.ascontiguousarray(vertex_colors, dtype=np.uint8)
    elif face_colors is not None:
        colors = np.ascontiguousarray(face_colors, dtype=np.uint8)
    else:
        colors = None

    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError("vertices must have shape (N, 3)")

    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError("faces must have shape (M, 3)")

    if faces.size and (faces.min() < 0 or faces.max() >= len(vertices)):
        raise ValueError("faces contains vertex indices out of range")

    poly_data = vtk.vtkPolyData()

    # Vertices
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(vertices, deep=True))
    poly_data.SetPoints(points)

    # Triangular faces
    offsets = np.arange(0, 3 * len(faces) + 1, 3, dtype=np.int64)
    connectivity = np.ascontiguousarray(faces.ravel(), dtype=np.int64)

    polys = vtk.vtkCellArray()
    polys.SetData(
        numpy_to_vtkIdTypeArray(offsets, deep=True),
        numpy_to_vtkIdTypeArray(connectivity, deep=True),
    )
    poly_data.SetPolys(polys)

    # colors
    if colors is not None:
        vtk_colors = numpy_to_vtk(colors, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        vtk_colors.SetNumberOfComponents(3)
        vtk_colors.SetName("Colors")
        if vertex_colors is not None:
            poly_data.GetPointData().SetScalars(vtk_colors)
        elif face_colors is not None:
            poly_data.GetCellData().SetScalars(vtk_colors)

    # ids
    if vertex_ids is not None:
        vtk_ids = numpy_to_vtk(np.ascontiguousarray(vertex_ids), deep=True)
        vtk_ids.SetName("vertex_id")
        poly_data.GetPointData().AddArray(vtk_ids)

    if face_ids is not None:
        vtk_ids = numpy_to_vtk(np.ascontiguousarray(vertex_ids), deep=True)
        vtk_ids.SetName("face_id")
        poly_data.GetCellData().AddArray(vtk_ids)

    return poly_data


def from_vtk_poly_data_to_mesh(vtk_poly_data):
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
    vertices = vtk_to_numpy(
        vtk_poly_data.GetPoints().GetData()
    )

    cell_array = vtk_poly_data.GetPolys()
    connectivity = vtk_to_numpy(cell_array.GetConnectivityArray())
    # Reconstruct faces (assuming triangles like your original reshape)
    faces = connectivity.reshape(-1, 3)

    point_colors = vtk_poly_data.GetPointData().GetScalars()
    cell_colors = vtk_poly_data.GetCellData().GetScalars()

    colors_array = None
    if point_colors is not None:
        colors_array = point_colors
    elif cell_colors is not None:
        colors_array = cell_colors

    if colors_array is None:
        colors = None
    else:
        colors = vtk_to_numpy(colors_array)

    point_ids = vtk_poly_data.GetPointData().GetArray("vertex_id")
    cell_ids = vtk_poly_data.GetCellData().GetArray("face_id")

    vertex_ids = vtk_to_numpy(point_ids) if point_ids is not None else None
    face_ids = vtk_to_numpy(cell_ids) if cell_ids is not None else None

    return vertices, faces, colors, vertex_ids, face_ids


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
            get_vtk_array_type(data_matrix.dtype)
        )
        image_data.SetNumberOfScalarComponents(1)
        image_data.AllocateScalars()
    else:
        image_data.AllocateScalars(
            get_vtk_array_type(data_matrix.dtype), 1
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
