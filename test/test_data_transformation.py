# -*- python -*-
#
#       test_data_transformation.py : 
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
import numpy

#       ========================================================================
#       Local Import 
import alinea.phenomenal.data_transformation

#       ========================================================================
#       Code


def test_data_transformation():
    matrix = numpy.ones((10, 10, 10), dtype=numpy.uint8)
    radius = 8

    points_3d = alinea.phenomenal.data_transformation.matrix_to_points_3d(
        matrix, radius, [0, 0, 0])

    assert points_3d[0] == (0., 0., 0.)
    assert points_3d[1] == (0., 0., 16.)
    assert len(points_3d) == matrix.size

    mat, _, _ = alinea.phenomenal.data_transformation.points_3d_to_matrix(
        points_3d, radius)

    assert mat.ndim == 3
    assert mat.size == matrix.size
    assert (mat == matrix).all()

    print alinea.phenomenal.data_transformation.limit_points_3d(points_3d)


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_data_transformation()
