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

    cubes = alinea.phenomenal.data_transformation.matrix_to_cubes(
        matrix, 8, [0, 0, 0])

    assert cubes[0].radius == 8
    assert (cubes[0].position == [0., 0., 0.]).all()
    assert len(cubes) == matrix.size

    mat = alinea.phenomenal.data_transformation.cubes_to_matrix(cubes)
    assert mat.ndim == 3
    assert mat.size == matrix.size
    assert (mat == matrix).all()

    print alinea.phenomenal.data_transformation.limit_cubes(cubes)


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_data_transformation()
