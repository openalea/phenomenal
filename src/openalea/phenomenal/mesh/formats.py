# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import vtk
import vtkmodules.util.numpy_support
import vtkmodules

from .vtk_transformation import from_vertices_faces_to_vtk_poly_data
# ==============================================================================

__all__ = [
    "write_vertices_faces_to_ply_file",
    "write_vtk_poly_data_to_ply_file",
    "read_ply_to_vertices_faces",
    "read_ply_to_vtk_poly_data",
]

# ==============================================================================


def write_vertices_faces_to_ply_file(
    filename, vertices, faces, vertices_colors=None, faces_colors=None
) -> None:
    """
    Write methods to save vertices and faces in ply format.

    Parameters
    ----------
    filename: str
        The name of the file to write to. Should be ending with .ply
    vertices: list[tuple]
        An array of vertex positions.
    faces: list[tuple]
        An array of faces id.
    vertices_colors: list[tuple] (optional)
        An array of RGB color for each vertex.
    faces_colors: list[tuple] (optional)
        An array of RGB color for each face.
    Returns
    -------
    None
    """

    vtk_poly_data = from_vertices_faces_to_vtk_poly_data(
        vertices, faces, vertices_colors=vertices_colors, faces_colors=faces_colors
    )

    write_vtk_poly_data_to_ply_file(filename, vtk_poly_data)


def read_ply_to_vertices_faces(filename):
    """
    Read ply file to vertices and faces

    Parameters
    ----------
    filename: str
        The filename of a ply model

    Returns
    -------
    mesh: tuple
        A tuple with vertices, faces and color of the mesh.
    """

    ply_reader = vtk.vtkPLYReader()
    ply_reader.SetFileName(filename)
    ply_reader.Update()

    vtk_poly_data = ply_reader.GetOutput()

    vertices = vtkmodules.util.numpy_support.vtk_to_numpy(
        vtk_poly_data.GetPoints().GetData()
    )

    faces = vtkmodules.util.numpy_support.vtk_to_numpy(
        vtk_poly_data.GetPolys().GetData()
    )

    faces = faces.reshape((len(faces) // 4, 4))

    colors = vtk_poly_data.GetPointData().GetScalars()
    if colors is not None:
        colors = vtkmodules.util.numpy_support.vtk_to_numpy(colors)

    return vertices, faces[:, 1:], colors


def write_vtk_poly_data_to_ply_file(filename, vtk_poly_data) -> None:
    """
    Write a vtk poly data to a ply file.

    Parameters
    ----------
    filename: str
        The name of the file to write to.
    vtk_poly_data: vtkPolyData
        The vtkPolyData object.

    Returns
    -------
    None
    """
    ply_writer = vtk.vtkPLYWriter()
    ply_writer.SetFileTypeToASCII()
    ply_writer.SetFileName(filename)
    ply_writer.SetInputData(vtk_poly_data)
    ply_writer.SetArrayName("Colors")
    ply_writer.Write()


def read_ply_to_vtk_poly_data(filename):
    """
    Reads the content of a ply file to a vtkPolyData object.

    Parameters
    ----------
    filename: str
        The name of the file to read.
    Returns
    -------
    polydata: vtkPolyData
        A poly data object
    """
    ply_reader = vtk.vtkPLYReader()
    ply_reader.SetFileName(filename)
    ply_reader.Update()

    return ply_reader.GetOutput()
