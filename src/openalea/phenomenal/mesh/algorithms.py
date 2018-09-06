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

import vtk
import vtk.util.numpy_support
import numpy
import math
import skimage.measure

from .vtk_transformation import (
    from_numpy_matrix_to_vtk_image_data,
    from_vtk_poly_data_to_vertices_faces,
    from_vertices_faces_to_vtk_poly_data,
    from_vtk_image_data_to_voxels_center)

# ==============================================================================

__all__ = ["meshing",
           "marching_cubes",
           "smoothing",
           "decimation",
           "voxelization",
           "mesh_surface_area",
           "from_vertices_faces_to_voxels_position"]

# ==============================================================================


def meshing(image_3d, smoothing_iteration=0, reduction=0.0, verbose=False):
    """
    Build a polygonal mesh representation (= list of vertices and faces) 
    from a 3d image (= numpy array 3D).
    
    More, some option, is available to smooth the 3D object representation and 
    reduce the number triangle.

    Firstly :
        A marching cubes algorithm is apply to compute the polygonal mesh.

    Secondly :
        A smoothing algorithm is apply according the number of iteration
        given

    Thirdly :
        A mesh decimation algorithm is apply according the percentage of
        reduction given.

    Parameters
    ----------
    
    image_3d : 3D numpy array
        3D Array with positive values 
        
    smoothing_iteration : int, optional
        Number of iteration for smoothing

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

    if image_3d.size < 8:
        raise ValueError("image_3d must have size >= 8")

    image_3d = image_3d.astype(numpy.uint8)

    vtk_image_data = from_numpy_matrix_to_vtk_image_data(
        image_3d)

    vtk_poly_data = marching_cubes(vtk_image_data, verbose=verbose)

    if smoothing_iteration > 1:
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

    vertices, faces, color = from_vtk_poly_data_to_vertices_faces(
        vtk_poly_data)
    vertices = vertices * image_3d.voxels_size + image_3d.world_coordinate

    return vertices, faces


def marching_cubes(vtk_image_data, iso_value=0.5, verbose=False):
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
        print(("=" * 80 + "\n" +
               "Marching cubes : \n"
               "\tIso value :{}\n").format(iso_value))

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

        print(("\tThere are {} points.\n"
               "\tThere are {} polygons.\n"
               + "=" * 80).format(vtk_poly_data.GetNumberOfPoints(),
                                  vtk_poly_data.GetNumberOfPolys()))

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
        print(("=" * 80 + "\n" +
               "Smoothing : \n"
               "\tFeature angle :{}\n"
               "\tNumber of iteration :{}\n"
               "\tPass band : {}\n\n" +
               "=" * 80).format(feature_angle, number_of_iteration, pass_band))

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

        print(("=" * 80 + "\n" +
               "Decimation : \n"
               "\tReduction (percentage) :{}\n"
               "\n"
               "\tBefore decimation\n"
               "\t-----------------\n"
               "\tThere are {} points.\n"
               "\tThere are {} polygons.\n").format(
            reduction,
            vtk_poly_data.GetNumberOfPoints(),
            vtk_poly_data.GetNumberOfPolys()))

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
        print(("\tAfter decimation\n"
               "\t-----------------\n"
               "\tThere are {} points.\n"
               "\tThere are {} polygons.\n" +
               80 * "=").format(reduction,
                                vtk_poly_data.GetNumberOfPoints(),
                                vtk_poly_data.GetNumberOfPolys()))

    return vtk_poly_decimated


def voxelization(vtk_poly_data, voxels_size=1):
    """
    Transform a mesh vtk poly data mesh representation objet to a list of 
    voxels position, according to a voxels size float.
    
    Parameters
    ----------
    vtk_poly_data : vtkPolyData
        vtkPolyData is a data object that is a concrete implementation of
        vtkDataSet. vtkPolyData represents a geometric structure consisting
        of vertices, lines, polygons, and/or triangle strips.
        Point and cell attribute values (e.g., scalars, vectors, etc.)
        also are represented.

    voxels_size : float, optional
        Size of the voxels

    verbose : bool, optional
        If True, print for some information of each part of the algorithms

    Returns
    -------
    vtk_image_data : vtkImageData
        Topologically and geometrically regular array of data

        vtkImageData is a data object that is a concrete implementation of 
        vtkDataSet. vtkImageData represents a geometric structure that is a 
        topological and geometrical regular array of points. 
        Examples include volumes (voxel data) and pixmaps
    
    """
    # ==========================================================================
    # Build White Image
    white_image = vtk.vtkImageData()

    bounds = [0.0] * 6
    vtk_poly_data.GetBounds(bounds)

    # desired volume spacing
    spacing = [voxels_size, voxels_size, voxels_size]
    white_image.SetSpacing(spacing)

    # ==========================================================================
    # compute dimensions

    dim = [0] * 3
    for i in range(3):
        dim[i] = int(math.ceil(
            (bounds[i * 2 + 1] - bounds[i * 2]) / spacing[i]))

    white_image.SetDimensions(dim)
    white_image.SetExtent(0, dim[0] - 1, 0, dim[1] - 1, 0, dim[2] - 1)

    origin = [0.0] * 3
    for i in range(3):
        origin[i] = bounds[i * 2] + spacing[i] / 2.0

    white_image.SetOrigin(origin)

    # ==========================================================================

    white_image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    inval = 255
    outval = 0

    count = white_image.GetNumberOfPoints()
    for i in range(count):
        white_image.GetPointData().GetScalars().SetTuple1(i, inval)

    # ==========================================================================
    # polygonal data --> image stencil:

    edges = vtk.vtkFeatureEdges()
    edges.SetInputData(vtk_poly_data)
    edges.FeatureEdgesOff()
    edges.NonManifoldEdgesOn()
    edges.BoundaryEdgesOn()
    edges.Update()

    pol2stenc = vtk.vtkPolyDataToImageStencil()
    pol2stenc.SetOutputOrigin(origin)
    pol2stenc.SetInputData(vtk_poly_data)
    pol2stenc.SetOutputSpacing(spacing)
    pol2stenc.SetOutputWholeExtent(white_image.GetExtent())
    pol2stenc.Update()

    vtk.vtkCleanPolyData()


    # ==========================================================================
    # Cut the corresponding white image and set the background:

    imgstenc = vtk.vtkImageStencil()
    imgstenc.SetInputData(white_image)
    imgstenc.SetStencilConnection(pol2stenc.GetOutputPort())
    imgstenc.ReverseStencilOff()
    imgstenc.SetBackgroundValue(outval)
    imgstenc.Update()

    # ==========================================================================

    return imgstenc.GetOutput()


def mesh_surface_area(vertices,
                      faces):
    """ Return the surface_area of a mesh

    :param vertices:
    :param faces:
    :return:
    """
    return skimage.measure.mesh_surface_area(vertices, faces)


def from_vertices_faces_to_voxels_position(vertices,
                                           faces,
                                           voxels_size=4):

    poly_data = from_vertices_faces_to_vtk_poly_data(vertices, faces)
    image_data = voxelization(poly_data, voxels_size=voxels_size)
    voxels_position = from_vtk_image_data_to_voxels_center(image_data)

    return voxels_position
