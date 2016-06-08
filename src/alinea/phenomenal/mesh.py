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
import skimage.measure
import vtk
import vtk.util.numpy_support

from alinea.phenomenal.data_transformation import (
    vtk_poly_data_to_vertices_faces,
    vertices_faces_to_vtk_poly_data,
    points_3d_to_matrix,
    numpy_matrix_to_vtk_image_data,
    voxel_centers_to_sparse_matrix)

# ==============================================================================


def deprecated_mesh(voxel_centers, voxel_size):
    """
    Build a  polygonal mesh representation (vertices and faces) from voxels.

    A marching cubes algorithm is apply to compute the polygonal mesh.

    Parameters
    ----------
    voxel_centers : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    Returns
    -------
    vertices : [(x, y, z), ...]
        Spatial coordinates for unique mesh vertices.

    faces : [(V1, V2, V3), ...]
        Define triangular faces via referencing vertex indices from vertices.
        This algorithm specifically outputs triangles, so each face has exactly
        three indices
    """
    matrix, real_origin = points_3d_to_matrix(voxel_centers, voxel_size)

    if len(matrix.shape) != 3 or matrix.shape < (2, 2, 2):
        return list(), list()

    vertices, faces = skimage.measure.marching_cubes(matrix, 0.5)

    faces = skimage.measure.correct_mesh_orientation(
        matrix, vertices, faces, gradient_direction='descent')

    vertices = vertices * voxel_size + real_origin

    return vertices, faces


def meshing(voxel_centers, voxel_size,
            smoothing_iteration=0, reduction=0.0, verbose=False):
    """
    Build a  polygonal mesh representation (vertices and faces) from voxels.

    Firstly :
        A marching cubes algorithm is apply to compute the polygonal mesh.

    Secondly :
        A smoothing algorithm is apply according the number of iteration
        indicate/

    Thirdly :
        A mesh decimation algorithm is apply according the percentage of
        reduction indicate.

    Parameters
    ----------
    voxel_centers : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    smoothing_iteration : int, optional


    reduction : float, optional
        Center position of the first original voxel, who will be split.
        0 and 1

    verbose : bool, optional
        If True, print for some information of each part of the algorithms

    Returns
    -------
    vertices : [(x, y, z), ...]
        Spatial coordinates for unique mesh vertices.

    faces : [(V1, V2, V3), ...]
        Define triangular faces via referencing vertex indices from vertices.
        This algorithm specifically outputs triangles, so each face has exactly
        three indices
    """

    if not voxel_centers or len(voxel_centers) < 10:
        return list(), list()

    matrix, real_origin = points_3d_to_matrix(voxel_centers, voxel_size)
    # matrix, real_origin = voxel_centers_to_sparse_matrix(
    #     voxel_centers, voxel_size)

    vtk_image_data = numpy_matrix_to_vtk_image_data(matrix)

    vtk_poly_data = marching_cubes(vtk_image_data, verbose=verbose)

    if 1 < smoothing_iteration:
        vtk_poly_data = smoothing(
            vtk_poly_data,
            number_of_iteration=smoothing_iteration,
            verbose=verbose)

    if 0.0 < reduction < 1.0:
        vtk_poly_data = decimation(
            vtk_poly_data,
            reduction=reduction,
            verbose=verbose)

    if vtk_poly_data.GetNumberOfPoints() == 0:
        return list(), list()

    vertices, faces = vtk_poly_data_to_vertices_faces(vtk_poly_data)
    vertices = vertices * voxel_size + real_origin

    return vertices, faces


def marching_cubes(vtk_image_data, iso_value=1.0, verbose=False):
    """
    Call of vtkMarchingCubes on a vtk_image_data with iso_value

    vtkMarchingCubes is a filter that takes as input a volume
    (e.g., 3D structured point set) and generates on output one or more
    isosurfaces.

    One or more contour values must be specified to generate the isosurfaces.
    Alternatively, you can specify a min/max scalar range and the number of
    contours to generate a series of evenly spaced contour values.

    Parameters
    ----------
    vtk_image_data : vtkImageData
        vtkImageData is a data object that is a concrete implementation of
        vtkDataSet. vtkImageData represents a geometric structure that is a
        topological and geometrical regular array of points. Examples include
        volumes (voxel data) and pixmaps.

    iso_value : float, optional
        Contour value to search for isosurfaces in volume.

    verbose : bool, optional
        If True, print for some information of each part of the algorithms

    Returns
    -------
    put : vtkPolyData
        vtkPolyData is a data object that is a concrete implementation of
        vtkDataSet. vtkPolyData represents a geometric structure consisting
        of vertices, lines, polygons, and/or triangle strips.
        Point and cell attribute values (e.g., scalars, vectors, etc.)

    """

    if verbose:
        print "================================================================"
        print "Marching cubes :"
        print "\tIso value :", iso_value
        print ""

    surface = vtk.vtkMarchingCubes()
    if vtk.VTK_MAJOR_VERSION <= 5:
        surface.SetInput(vtk_image_data)
    else:
        surface.SetInputData(vtk_image_data)

    surface.ComputeNormalsOn()
    surface.SetValue(0, iso_value)
    surface.Update()

    vtk_poly_data = surface.GetOutput()

    if verbose:
        print "\tThere are", vtk_poly_data.GetNumberOfPoints(), "points."
        print "\tThere are", vtk_poly_data.GetNumberOfPolys(), "polygons.\n"
        print "================================================================"

    return vtk_poly_data


def smoothing(vtk_poly_data,
              feature_angle=120.0,
              number_of_iteration=5,
              pass_band=0.01,
              verbose=False):
    """
    Call of vtkWindowedSincPolyDataFilter on a vtk_poly_data to smoothing the
    edge of poly_data


    Parameters
    ----------
    vtk_poly_data : vtkPolyData
        vtkPolyData is a data object that is a concrete implementation of
        vtkDataSet. vtkPolyData represents a geometric structure consisting
        of vertices, lines, polygons, and/or triangle strips.
        Point and cell attribute values (e.g., scalars, vectors, etc.)
        also are represented.

    feature_angle : float, optional
        Feature angle for sharp edge identification.

    number_of_iteration : float, optional
        Number of iteration of smoothing

    pass_band : float, optional
        Passband value for the windowed sinc filter

    verbose : bool, optional
        If True, print for some information of each part of the algorithms

    Returns
    -------
    out : vtkPolyData
        vtkPolyData is a data object that is a concrete implementation of
        vtkDataSet. vtkPolyData represents a geometric structure consisting
        of vertices, lines, polygons, and/or triangle strips.
        Point and cell attribute values (e.g., scalars, vectors, etc.)
    """

    if verbose:
        print "================================================================"
        print "Smoothing :"
        print "\tFeature angle :", feature_angle
        print "\tNumber of iteration :", number_of_iteration
        print "\tPass band :", pass_band
        print ""
        print "================================================================"

    smoother = vtk.vtkWindowedSincPolyDataFilter()

    if vtk.VTK_MAJOR_VERSION <= 5:
        smoother.SetInput(vtk_poly_data)
    else:
        smoother.SetInputData(vtk_poly_data)

    smoother.BoundarySmoothingOn()
    smoother.SetFeatureAngle(feature_angle)
    smoother.SetPassBand(pass_band)
    smoother.SetNumberOfIterations(number_of_iteration)
    smoother.Update()

    return smoother.GetOutput()


def decimation(vtk_poly_data, reduction=0.95, verbose=False):
    """
    Call of vtkQuadricDecimation on a vtk_poly_data to decimate the mesh

    Parameters
    ----------
    vtk_poly_data : vtkPolyData
        vtkPolyData is a data object that is a concrete implementation of
        vtkDataSet. vtkPolyData represents a geometric structure consisting
        of vertices, lines, polygons, and/or triangle strips.
        Point and cell attribute values (e.g., scalars, vectors, etc.)
        also are represented.

    reduction : float, optional
        Percentage of reduction for the decimation 0.95 will reduce the
        vtk_poly_date of 95%

    verbose : bool, optional
        If True, print for some information of each part of the algorithms

    Returns
    -------
    out : vtkPolyData
        vtkPolyData is a data object that is a concrete implementation of
        vtkDataSet. vtkPolyData represents a geometric structure consisting
        of vertices, lines, polygons, and/or triangle strips.
        Point and cell attribute values (e.g., scalars, vectors, etc.)
    """
    if verbose:
        print "================================================================"
        print "Decimation :"
        print "\tReduction (percentage) :", reduction
        print ""
        print "\tBefore decimation"
        print "\t-----------------"
        print "\tThere are", vtk_poly_data.GetNumberOfPoints(), "points."
        print "\tThere are", vtk_poly_data.GetNumberOfPolys(), "polygons.\n"

    decimate = vtk.vtkQuadricDecimation()
    decimate.SetTargetReduction(reduction)

    if vtk.VTK_MAJOR_VERSION <= 5:
        decimate.SetInputConnection(vtk_poly_data.GetProducerPort())
        decimate.SetInput(vtk_poly_data)
    else:
        decimate.SetInputData(vtk_poly_data)

    decimate.Update()

    vtk_poly_decimated = vtk.vtkPolyData()
    vtk_poly_decimated.ShallowCopy(decimate.GetOutput())

    if verbose:
        print "\tAfter decimation"
        print "\t-----------------"
        print "\tThere are", vtk_poly_decimated.GetNumberOfPoints(), "points."
        print "\tThere are", vtk_poly_decimated.GetNumberOfPolys(),
        print "polygons."
        print "================================================================"

    return vtk_poly_decimated


def compute_normal(vertices, faces):
    """
    Compute normal of each faces

    Parameters
    ----------
    vertices : [(x, y, z), ...]
        Spatial coordinates for unique mesh vertices.

    faces : [(V1, V2, V3), ...]
        Define triangular faces via referencing vertex indices from vertices.
        This algorithm specifically outputs triangles, so each face has exactly
        three indices

    Returns
    -------
    out : [(x, y, z), ...]
        List of vector direction of the normal in the same order that faces
    """

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
    """
    Compute center of each faces

    Parameters
    ----------
    vertices : [(x, y, z), ...]
        Spatial coordinates for unique mesh vertices.

    faces : [(V1, V2, V3), ...]
        Define triangular faces via referencing vertex indices from vertices.
        This algorithm specifically outputs triangles, so each face has exactly
        three indices

    Returns
    -------
    out : [(x, y, z), ...]
        List of center of faces  in the same order that faces
    """
    actual_vertices = vertices[faces]

    center = (actual_vertices[:, 0, :] +
              actual_vertices[:, 1, :] +
              actual_vertices[:, 2, :]) / 3.0

    return center


def write_on_ply_format(vertices, faces, filename):

    vtk_poly_data = vertices_faces_to_vtk_poly_data(vertices, faces)

    ply_writer = vtk.vtkPLYWriter()
    ply_writer.SetFileTypeToASCII()
    ply_writer.SetFileName(filename + '.ply')
    ply_writer.SetInputData(vtk_poly_data)
    ply_writer.Write()
