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
import skimage.measure
import numpy
import vtk
import vtk.util.numpy_support
# ==============================================================================


def meshing(matrix, origin, voxel_size):

    if len(matrix.shape) != 3 or matrix.shape < (2, 2, 2):
        return list(), list()

    vertices, faces = skimage.measure.marching_cubes(matrix, 0.5)

    faces = skimage.measure.correct_mesh_orientation(
        matrix, vertices, faces, gradient_direction='descent')

    vertices = vertices * voxel_size + origin

    return vertices, faces


def create_poly_data(vertices, faces):
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


def create_vertices_faces(poly_data):
    vertices = vtk.util.numpy_support.vtk_to_numpy(
        poly_data.GetPoints().GetData())

    faces = vtk.util.numpy_support.vtk_to_numpy(
        poly_data.GetPolys().GetData())

    faces = faces.reshape((len(faces) / 4, 4))

    return vertices, faces[:, 1:]


def mesh_decimation(poly_data, verbose=False):

    if verbose is True:
        print "Before decimation" \
            "\n-----------------\n" \
            "There are", poly_data.GetNumberOfPoints(), "points.\n" \
            "There are", poly_data.GetNumberOfPolys(), "polygons.\n"

    decimate = vtk.vtkQuadricDecimation()
    decimate.SetTargetReduction(0.99)
    decimate.SetInputData(poly_data)
    decimate.Update()

    poly_decimated = vtk.vtkPolyData()
    poly_decimated.ShallowCopy(decimate.GetOutput())

    print "After decimation" \
        "\n----------------\n" \
        "There are", poly_decimated.GetNumberOfPoints(), "points.\n" \
        "There are", poly_decimated.GetNumberOfPolys(), "polygons.\n"

    return poly_decimated


def compute_normal(vertices, faces):
    # Fancy indexing to define two vector arrays from triangle vertices
    actual_vertices = vertices[faces]
    a = actual_vertices[:, 0, :] - actual_vertices[:, 1, :]
    b = actual_vertices[:, 0, :] - actual_vertices[:, 2, :]

    # Find normal vectors for each face via cross product
    crosses = numpy.cross(a, b)
    crosses = crosses / (numpy.sum(
        crosses ** 2, axis=1) ** 0.5)[:, numpy.newaxis]

    return crosses


def center_of_vertices(vertices, faces):
    actual_vertices = vertices[faces]

    center = (actual_vertices[:, 0, :] +
              actual_vertices[:, 1, :] +
              actual_vertices[:, 2, :]) / 3.0

    return center
