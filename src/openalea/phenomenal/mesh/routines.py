# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import numpy
import cv2
# ==============================================================================

__all__ = ["meshing","voxelization","project_mesh_on_image", "median_color_from_images"]

from openalea.phenomenal.mesh import marching_cubes, smoothing, decimation, image_stencil
from openalea.phenomenal.object import Mesh, VoxelGrid, Image3D


# ==============================================================================


def median_color_from_images(vertices, faces, calibration, images):
    """Return the colors of each face according the median of their color list
    in the faces projected images.

    Parameters
    ----------

    vertices : [(x, y, z), ...]
        Spatial coordinates for unique mesh vertices.

    faces : [(V1, V2, V3), ...]
        Define triangular faces via referencing vertex indices from vertices.
        This algorithm specifically outputs triangles, so each face has exactly
        three indices

    calibration: projection function

    images: images[id_camera][angle] = image

    Returns
    -------

    """
    height, length, _ = images["side"][0].shape
    img = numpy.zeros((height, length), dtype=numpy.uint8)

    angles = numpy.array(range(0, 360, 30)).astype(float)

    colors = []
    for _, (i, j, k) in enumerate(faces):
        pt1, pt2, pt3 = vertices[i], vertices[j], vertices[k]
        arr = numpy.array([pt1, pt2, pt3])

        cc = []
        for angle in angles:
            pts = calibration.get_projection(angle)(arr).astype(int)
            if pts[0][1] == pts[1][1] == pts[2][1]:
                color = images["side"][angle][(pts[:, 0], pts[:, 1])]
            else:
                cv2.fillConvexPoly(img, pts, 255)
                print(img)
                index = numpy.where(img == 255)
                img[index] = 0
                color = images["side"][angle][index]
            cc.append(color)

        cc = numpy.concatenate(cc, axis=0)
        color = numpy.median(cc, axis=0).astype(int)
        colors.append(color)

    colors = list(map(tuple, colors))

    return colors


def project_mesh_on_image(vertices, faces, shape_image, projection):
    """
    Returns a binary image resulting of the projection of a mesh
    object representation (vertices, faces) with a projection
    function.

    Parameters
    ----------
    vertices: list
        A list of 3d points position
    faces: list
        A list of 3-tuple index vertices
    shape_image: tuple
        The shape of the image
    projection: fct
        projection function

    Returns
    -------
    image: numpy.ndarray
        A 2D numpy array
    """
    vertices = numpy.array(vertices)
    height, length = shape_image
    img = numpy.zeros((height, length), dtype=numpy.uint8)

    # triangles = []
    for i, j, k in faces:
        pt1, pt2, pt3 = vertices[i], vertices[j], vertices[k]
        arr = numpy.array([pt1, pt2, pt3])
        pts = projection(arr).astype(int)
        if pts[0][1] == pts[1][1] == pts[2][1]:
            continue
        cv2.fillConvexPoly(img, pts, 255)

    return img


def meshing(voxel_grid, smoothing_iteration=0, reduction=0.0, verbose=False):
    """
    Build a polygonal mesh representation
    from a voxel_grid

    More, some option, is available to smooth the 3D object representation and
    reduce the number triangle.

    Firstly :
        A marching cubes algorithm is applied to compute the polygonal mesh.

    Secondly :
        A smoothing algorithm is applied according the number of iteration
        given

    Thirdly :
        A mesh decimation algorithm is applied according the percentage of
        reduction given.

    Parameters
    ----------

    voxel_grid : 3a VoxelGrid object

    smoothing_iteration : int, optional
        Number of iteration for smoothing

    reduction : float, optional
        Center position of the first original voxel, who will be split.
        0 and 1

    verbose : bool, optional
        If True, print for some information of each part of the algorithms

    Returns
    -------
     Mesh
    """

    image_3d = voxel_grid.image_3d
    if image_3d.size < 8:
        raise ValueError("image_3d must have size >= 8")

    vtk_poly_data = marching_cubes(image_3d.vtk_image_data, verbose=verbose)

    if smoothing_iteration > 1:
        vtk_poly_data = smoothing(
            vtk_poly_data, number_of_iteration=smoothing_iteration, verbose=verbose
        )

    if 0.0 < reduction < 1.0:
        vtk_poly_data = decimation(vtk_poly_data, reduction=reduction, verbose=verbose)

    return Mesh(vtk_poly_data)


def voxelization(mesh, voxels_size=1):
    vtk_image = image_stencil(mesh.poly_data, spacing=voxels_size)
    image_3d = Image3D.from_vtk_image(vtk_image)
    return VoxelGrid.from_image_3d(image_3d, voxels_size=image_3d.voxels_size[0])