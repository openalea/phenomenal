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
from vtkmodules.util.numpy_support import vtk_to_numpy
import numpy as np

# ==============================================================================

__all__ = [
    "marching_cubes",
    "smoothing",
    "decimation",
    "image_stencil"
]

# ==============================================================================


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
        print(
            ("=" * 80 + "\n" + "Marching cubes : \n\tIso value :{}\n").format(iso_value)
        )

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
        print(
            ("\tThere are {} points.\n\tThere are {} polygons.\n" + "=" * 80).format(
                vtk_poly_data.GetNumberOfPoints(), vtk_poly_data.GetNumberOfPolys()
            )
        )

    return vtk_poly_data


def smoothing(
    vtk_poly_data,
    feature_angle=120.0,
    number_of_iteration=5,
    pass_band=0.01,
    verbose=False,
):
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
        print(
            (
                "=" * 80 + "\n" + "Smoothing : \n"
                "\tFeature angle :{}\n"
                "\tNumber of iteration :{}\n"
                "\tPass band : {}\n\n" + "=" * 80
            ).format(feature_angle, number_of_iteration, pass_band)
        )

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
        print(
            (
                "=" * 80 + "\n" + "Decimation : \n"
                "\tReduction (percentage) :{}\n"
                "\n"
                "\tBefore decimation\n"
                "\t-----------------\n"
                "\tThere are {} points.\n"
                "\tThere are {} polygons.\n"
            ).format(
                reduction,
                vtk_poly_data.GetNumberOfPoints(),
                vtk_poly_data.GetNumberOfPolys(),
            )
        )

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
        print(
            (
                "\tAfter decimation\n"
                "\t-----------------\n"
                "\tThere are {} points.\n"
                "\tThere are {} polygons.\n" + 80 * "="
            ).format(
                reduction,
                vtk_poly_data.GetNumberOfPoints(),
                vtk_poly_data.GetNumberOfPolys(),
            )
        )

    return vtk_poly_decimated


def image_stencil(vtk_poly_data, spacing=1):
    """Voxelize a closed mesh into a vtkImageData.

    Parameters
    ----------
    vtk_poly_data : vtk.vtkPolyData
        Input closed surface mesh.
    spacing : float or sequence of 3 floats, optional
        Voxel spacing along the x, y, and z axes. Defaults to 1.

    Returns
    -------
    vtk.vtkImageData
        Binary image with value 255 inside the mesh and 0 outside.
        The origin corresponds to the center of the first voxel.
    """
    if vtk_poly_data is None or vtk_poly_data.GetNumberOfPoints() == 0:
        raise ValueError("vtk_poly_data must contain points")

    spacing = np.asarray(spacing, dtype=float)
    if spacing.ndim == 0:
        spacing = np.full(3, spacing.item())
    if spacing.shape != (3,) or not np.all(np.isfinite(spacing)) or np.any(spacing <= 0):
        raise ValueError("spacing must be a positive scalar or 3-element sequence")

    # Mesh bounds: xmin, xmax, ymin, ymax, zmin, zmax.
    bounds = np.asarray(vtk_poly_data.GetBounds()).reshape(3, 2)

    # Number of voxels along each axis.
    dimensions = np.ceil(
        (bounds[:, 1] - bounds[:, 0]) / spacing
    ).astype(int)
    dimensions = np.maximum(dimensions, 1)

    # Position of the first voxel center.
    origin = bounds[:, 0] + spacing / 2

    # Initialize the image to 255 without a Python loop.
    white_image = vtk.vtkImageData()
    white_image.SetDimensions(*dimensions)
    white_image.SetSpacing(*spacing)
    white_image.SetOrigin(*origin)
    white_image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    scalars = vtk_to_numpy(white_image.GetPointData().GetScalars())
    scalars.fill(255)

    # Convert the mesh into an image stencil.
    poly_to_stencil = vtk.vtkPolyDataToImageStencil()
    poly_to_stencil.SetInputData(vtk_poly_data)
    poly_to_stencil.SetOutputOrigin(*origin)
    poly_to_stencil.SetOutputSpacing(*spacing)
    poly_to_stencil.SetOutputWholeExtent(white_image.GetExtent())

    # Apply the stencil: 0 outside, 255 inside.
    image_stencil = vtk.vtkImageStencil()
    image_stencil.SetInputData(white_image)
    image_stencil.SetStencilConnection(poly_to_stencil.GetOutputPort())
    image_stencil.SetBackgroundValue(0)
    image_stencil.Update()

    return image_stencil.GetOutput()
0

