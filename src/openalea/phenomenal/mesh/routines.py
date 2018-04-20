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

import numpy
import cv2
# ==============================================================================

__all__ = ["normals",
           "centers",
           "project_mesh_on_image",
           "median_color_from_images"]

# ==============================================================================


def median_color_from_images(vertices, faces, calibration, images):
    """ Return the colors of each faces according the median of their color list
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

    images: images[id_camera][angle] = imaga

    Returns
    -------

    """
    height, length, _ = images["side"][0].shape
    img = numpy.zeros((height, length), dtype=numpy.uint8)

    angles = numpy.array(range(0, 360, 30)).astype(float)

    colors = list()
    for ind, (i, j, k) in enumerate(faces):
        pt1, pt2, pt3 = vertices[i], vertices[j], vertices[k]
        arr = numpy.array([pt1, pt2, pt3])

        cc = list()
        for angle in angles:
            pts = calibration.get_projection(angle)(arr).astype(int)
            if pts[0][1] == pts[1][1] == pts[2][1]:
                color = images["side"][angle][(pts[:, 0], pts[:, 1])]
            else:
                cv2.fillConvexPoly(img, pts, 255)
                index = numpy.where(img == 255)
                img[index] = 0
                color = images["side"][angle][index]
            cc.append(color)

        cc = numpy.concatenate(cc, axis=0)
        color = numpy.median(cc, axis=0).astype(int)
        colors.append(color)

    colors = map(tuple, colors)

    return colors


def normals(vertices, faces):
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


def centers(vertices, faces):
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
    v = vertices[faces]

    return (v[:, 0, :] + v[:, 1, :] + v[:, 2, :]) / 3.0


def project_mesh_on_image(vertices, faces, shape_image, projection):
    """ Return a binary image resulting of the projection of a mesh
    object representation (vertices, faces) with a projection
    function.

    :param vertices: list of 3d points position
    :param faces: list of 3-tuple index vertices
    :param shape_image: shape of the image
    :param projection: projection function
    :return: 2D numpy array
    """
    vertices = numpy.array(vertices)
    height, length = shape_image
    img = numpy.zeros((height, length), dtype=numpy.uint8)

    # triangles = list()
    for i, j, k in faces:
        pt1, pt2, pt3 = vertices[i], vertices[j], vertices[k]
        arr = numpy.array([pt1, pt2, pt3])
        pts = projection(arr).astype(int)
        if pts[0][1] == pts[1][1] == pts[2][1]:
            continue
        else:
            cv2.fillConvexPoly(img, pts, 255)

    return img