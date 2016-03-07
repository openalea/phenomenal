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
import vtk
import vtk.util.numpy_support

from alinea.phenomenal.data_transformation import \
    (limit_points_3d, voxel_centers_to_vtk_image_data)
# ==============================================================================


def meshing(voxel_centers, voxel_size,
            smoothing=False, reduction=0.0, verbose=False):

    if not voxel_centers:
        return list(), list()

    vtk_image_data = voxel_centers_to_vtk_image_data(voxel_centers, voxel_size)

    vtk_poly_data = marching_cubes(vtk_image_data)

    if smoothing:
        vtk_poly_data = smoothing(vtk_poly_data)

    if 0.0 < reduction < 1.0:
        vtk_poly_data = decimation(
            vtk_poly_data, reduction=reduction, verbose=verbose)

    if vtk_poly_data.GetNumberOfPoints() == 0:
        return list(), list()

    x_min, y_min, z_min, x_max, y_max, z_max = limit_points_3d(voxel_centers)

    vertices, faces = vtk_poly_data_to_vertices_faces(vtk_poly_data)

    vertices = vertices * voxel_size + (x_min, y_min, z_min)

    return vertices, faces


def marching_cubes(vtk_image_data, iso_value=0.5):

    surface = vtk.vtkMarchingCubes()
    surface.SetInputData(vtk_image_data)
    surface.ComputeNormalsOn()
    surface.SetValue(0, iso_value)
    surface.Update()

    return surface.GetOutput()


def smoothing(vtk_poly_data,
                   feature_angle=120.0,
                   number_of_iteration=5,
                   pass_band=0.01):

    smoother = vtk.vtkWindowedSincPolyDataFilter()
    smoother.SetInputData(vtk_poly_data)
    smoother.BoundarySmoothingOn()
    smoother.SetFeatureAngle(feature_angle)
    smoother.SetPassBand(pass_band)
    smoother.SetNumberOfIterations(number_of_iteration)
    smoother.Update()

    return smoother.GetOutput()


def decimation(vtk_poly_data, reduction=0.95, verbose=False):

    if verbose:
        print "Before decimation" \
            "\n-----------------\n" \
            "There are", vtk_poly_data.GetNumberOfPoints(), "points.\n" \
            "There are", vtk_poly_data.GetNumberOfPolys(), "polygons.\n"

    decimate = vtk.vtkQuadricDecimation()
    decimate.SetTargetReduction(reduction)
    decimate.SetInputData(vtk_poly_data)
    decimate.Update()

    vtk_poly_decimated = vtk.vtkPolyData()
    vtk_poly_decimated.ShallowCopy(decimate.GetOutput())

    if verbose:
        print "After decimation" \
            "\n----------------\n" \
            "There are", vtk_poly_decimated.GetNumberOfPoints(), "points.\n" \
            "There are", vtk_poly_decimated.GetNumberOfPolys(), "polygons.\n"

    return vtk_poly_decimated


def vertices_faces_to_vtk_poly_data(vertices, faces):
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


def vtk_poly_data_to_vertices_faces(vtk_poly_data):
    vertices = vtk.util.numpy_support.vtk_to_numpy(
        vtk_poly_data.GetPoints().GetData())

    faces = vtk.util.numpy_support.vtk_to_numpy(
        vtk_poly_data.GetPolys().GetData())

    faces = faces.reshape((len(faces) / 4, 4))

    return vertices, faces[:, 1:]


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
