# -*- python -*-
#
#       mesh.py : 
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
#       ========================================================================

#       ========================================================================
#       External Import
import skimage.measure
import numpy

#       ========================================================================
#       Local Import 

#       ========================================================================
#       Code


def meshing(matrix, origin, radius):

    if len(matrix.shape) != 3 or matrix.shape < (2, 2, 2):
        return list(), list()

    vertices, faces = skimage.measure.marching_cubes(matrix, 0.0)

    faces = skimage.measure.correct_mesh_orientation(
        matrix, vertices, faces, gradient_direction='descent')

    vertices = vertices * radius * 2 + origin

    return vertices, faces


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

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    pass
