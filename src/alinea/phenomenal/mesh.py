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


def meshing(matrix):
    verts, faces = skimage.measure.marching_cubes(matrix, 0)

    faces = skimage.measure.correct_mesh_orientation(
        matrix, verts, faces, gradient_direction='descent')

    return verts, faces


def compute_normal(verts, faces):
     # Fancy indexing to define two vector arrays from triangle vertices
    actual_verts = verts[faces]
    a = actual_verts[:, 0, :] - actual_verts[:, 1, :]
    b = actual_verts[:, 0, :] - actual_verts[:, 2, :]

    # Find normal vectors for each face via cross product
    crosses = numpy.cross(a, b)
    crosses = crosses / (numpy.sum(
        crosses ** 2, axis=1) ** 0.5)[:, numpy.newaxis]

    return crosses


def center_of_vertice(verts, faces):
    actual_verts = verts[faces]

    center = (actual_verts[:, 0, :] +
              actual_verts[:, 1, :] +
              actual_verts[:, 2, :]) / 3.0

    return center

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    pass