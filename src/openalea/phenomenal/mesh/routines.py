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

__all__ = ["project_mesh_on_image", "median_color_from_images"]

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
