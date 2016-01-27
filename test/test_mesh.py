# -*- python -*-
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
# ==============================================================================
import numpy

import alinea.phenomenal.data_transformation
import alinea.phenomenal.mesh
# ==============================================================================


def test_mesh_1():
    size = 10
    origin = (0.0, 0.0, 0.0)
    radius = 5

    matrix = numpy.zeros((size, size, size), dtype=numpy.uint8)
    matrix[1:9, 1:9, 1:9] = 1
    vertices, faces = alinea.phenomenal.mesh.meshing(matrix, origin, radius)


def test_mesh_2():

    radius = 8
    points_3d = list()

    mat, index, origin = alinea.phenomenal.data_transformation.\
        points_3d_to_matrix(points_3d, radius)

    vertices, faces = alinea.phenomenal.mesh.meshing(mat, origin, radius)

    assert vertices == list()
    assert faces == list()


def test_mesh_3():

    radius = 1
    points_3d = list()
    points_3d.append((0, 0, 0))
    points_3d.append((1, 1, 2))

    mat, index, origin = alinea.phenomenal.data_transformation.\
        points_3d_to_matrix(points_3d, radius)

    vertices, faces = alinea.phenomenal.mesh.meshing(mat, origin, radius)

# ==============================================================================

if __name__ == "__main__":
    test_mesh_1()
    test_mesh_2()
    test_mesh_3()
