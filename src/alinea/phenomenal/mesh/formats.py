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
    from_vertices_faces_to_vtk_poly_data)
# ==============================================================================

__all__ = ["write_vertices_faces_to_ply_file",
           "write_vtk_poly_data_to_ply_file",
           "write_vertices_faces_to_json_file",
           "read_json_file_to_vertices_faces"]

# ==============================================================================


def write_vertices_faces_to_ply_file(vertices, faces, filename):
    vtk_poly_data = from_vertices_faces_to_vtk_poly_data(vertices, faces)

    ply_writer = vtk.vtkPLYWriter()
    ply_writer.SetFileTypeToASCII()
    ply_writer.SetFileName(filename + '.ply')
    ply_writer.SetInputData(vtk_poly_data)
    ply_writer.Write()


def write_vtk_poly_data_to_ply_file(vtk_poly_data, filename):

    ply_writer = vtk.vtkPLYWriter()
    ply_writer.SetFileTypeToASCII()
    ply_writer.SetFileName(filename + '.ply')
    ply_writer.SetInputData(vtk_poly_data)
    ply_writer.Write()


def write_vertices_faces_to_json_file(vertices, faces, mesh_path):
    mesh_path = os.path.realpath(mesh_path)
    path_directory, file_name = os.path.split(mesh_path)

    if not os.path.exists(path_directory):
        os.makedirs(path_directory)

    with open(mesh_path, 'w') as outfile:
        json.dump({'vertices': vertices.tolist(),
                   'faces': faces.tolist()}, outfile)


def read_json_file_to_vertices_faces(file_path):
    with open(file_path, 'r') as infile:
        load_mesh = json.load(infile)

    return numpy.array(load_mesh['vertices']), numpy.array(load_mesh['faces'])
