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
import collections

import alinea.phenomenal.data_transformation
# ==============================================================================


def test_data_transformation_1():
    matrix = numpy.ones((10, 10, 10), dtype=numpy.uint8)
    radius = 8
    origin = (1, 2, 3)

    points_3d = alinea.phenomenal.data_transformation.\
        matrix_to_points_3d(matrix, radius, origin)

    assert points_3d[0] == (1., 2., 3.)
    assert points_3d[1] == (1., 2., 19.)
    assert len(points_3d) == matrix.size

    mat, index, origin = alinea.phenomenal.data_transformation.\
        points_3d_to_matrix(points_3d, radius)

    assert mat.ndim == 3
    assert mat.size == matrix.size
    assert (mat == matrix).all()
    assert origin == (1, 2, 3)


def test_limit_points_empty():

    points_3d = list()
    x_min, y_min, z_min, x_max, y_max, z_max = \
        alinea.phenomenal.data_transformation.limit_points_3d(points_3d)

    assert x_min is None
    assert x_max is None
    assert y_min is None
    assert y_max is None
    assert z_min is None
    assert z_max is None


def test_limit_points_one_value():

    points_3d = list()
    points_3d.append((0.1, 0.2, 0.3))

    x_min, y_min, z_min, x_max, y_max, z_max = \
        alinea.phenomenal.data_transformation.limit_points_3d(points_3d)

    assert x_min == 0.1
    assert y_min == 0.2
    assert z_min == 0.3

    assert x_max == 0.1
    assert y_max == 0.2
    assert z_max == 0.3


def test_limit_points_many_values():
    points_3d = list()

    nb_value = 50
    for i in range(nb_value):
        for j in range(nb_value):
            for k in range(nb_value):
                points_3d.append((i, j, k))

    x_min, y_min, z_min, x_max, y_max, z_max = \
        alinea.phenomenal.data_transformation.limit_points_3d(points_3d)

    assert x_min == 0
    assert y_min == 0
    assert z_min == 0

    assert x_max == nb_value - 1
    assert y_max == nb_value - 1
    assert z_max == nb_value - 1


def test_data_transformation_2():

    radius = 8
    points_3d = list()

    mat, index, origin = alinea.phenomenal.data_transformation.\
        points_3d_to_matrix(points_3d, radius)

    assert index == list()
    assert origin == (None, None, None)

    points_3d = alinea.phenomenal.data_transformation.\
        matrix_to_points_3d(mat, radius, origin)

    assert points_3d == list()


def test_data_transformation_3():

    radius = 8
    points_3d = list()
    points_3d.append((1, 42, 1))

    mat, index, origin = alinea.phenomenal.data_transformation.\
        points_3d_to_matrix(points_3d, radius)

    assert mat == [[[1]]]
    assert index[0] == (0, 0, 0)
    assert origin == (1, 42, 1)

    points_3d = alinea.phenomenal.data_transformation.\
        matrix_to_points_3d(mat, radius, origin)

    assert len(points_3d) == 1
    assert points_3d[0] == (1, 42, 1)


def test_remove_internal_points_3d_1():

    radius = 4
    points_3d = collections.deque()

    points_3d = alinea.phenomenal.data_transformation.remove_internal_points_3d(
        points_3d, radius)

    assert points_3d == collections.deque()

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_data_transformation_1()
    test_limit_points_empty()
    test_limit_points_one_value()
    test_limit_points_many_values()
    test_data_transformation_2()
    test_data_transformation_3()
    test_remove_internal_points_3d_1()
