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
import os
import json
import numpy

from alinea.phenomenal.mesh.vtk_transformation import (
    from_vertices_faces_to_vtk_poly_data,
    from_vtk_poly_data_to_vertices_faces)
# ==============================================================================

__all__ = ["write_vertices_faces_to_ply_file",
           "write_vtk_poly_data_to_ply_file",
           "write_vertices_faces_to_json_file",
           "read_json_file_to_vertices_faces"]

# ==============================================================================


def write_vertices_faces_to_ply_file(filename, vertices, faces):
    """
    Write methods to save vertices and faces in ply format. 
    """
    vtk_poly_data = from_vertices_faces_to_vtk_poly_data(vertices, faces)

    ply_writer = vtk.vtkPLYWriter()
    ply_writer.SetFileTypeToASCII()
    ply_writer.SetFileName(filename)
    ply_writer.SetInputData(vtk_poly_data)
    ply_writer.Write()


def read_ply_to_vertices_faces(filename):
    """
    Read ply file to vertices and faces
    """

    poly_data = read_ply_to_vtk_poly_data(filename)

    vertices, faces = from_vtk_poly_data_to_vertices_faces(poly_data)

    return vertices, faces


def write_vtk_poly_data_to_ply_file(filename, vtk_poly_data):

    ply_writer = vtk.vtkPLYWriter()
    ply_writer.SetFileTypeToASCII()
    ply_writer.SetFileName(filename)
    ply_writer.SetInputData(vtk_poly_data)
    ply_writer.Write()


def read_ply_to_vtk_poly_data(filename):

    ply_reader = vtk.vtkPLYReader()
    ply_reader.SetFileName(filename)
    ply_reader.Update()

    return ply_reader.GetOutput()


def write_vertices_faces_to_json_file(filename, vertices, faces):
    filename = os.path.realpath(filename)
    path_directory, file_name = os.path.split(filename)

    if not os.path.exists(path_directory):
        os.makedirs(path_directory)

    with open(filename, 'w') as outfile:
        json.dump({'vertices': vertices.tolist(),
                   'faces': faces.tolist()}, outfile)


def read_json_file_to_vertices_faces(filename):

    with open(filename, 'r') as infile:
        load_mesh = json.load(infile)

    return numpy.array(load_mesh['vertices']), numpy.array(load_mesh['faces'])
