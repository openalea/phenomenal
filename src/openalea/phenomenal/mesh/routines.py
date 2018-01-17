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
import cv2
# ==============================================================================

__all__ = ["normals", "centers"]

# ==============================================================================


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


def project_mesh_on_image(vertices, faces, shape_image, projection,
                          with_morphology_close=True):

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
        # triangles.append()

    # cv2.fillPoly(img, triangles, 255)

    # if with_morphology_close:
    #     kernel = numpy.ones((3, 3), numpy.uint8)
    #     img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    return img