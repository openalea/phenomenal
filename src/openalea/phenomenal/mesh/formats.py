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


from .vtk_transformation import from_mesh_to_vtk_poly_data
# ==============================================================================

__all__ = [
    "write_ply",
    "read_ply",
]

# ==============================================================================




def write_ply(filename, vtk_poly_data) -> None:
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
    ply_writer.Write()


def read_ply(filename):
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
