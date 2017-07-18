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

from alinea.phenomenal.multi_view_reconstruction.multi_view_reconstruction\
    import (split_voxel_centers_in_eight)
# ==============================================================================


def test_simply_working_1():

    voxels_size = 16
    voxels_position = numpy.array([[0.0, 0.0, 0.0]])

    res = split_voxel_centers_in_eight(voxels_position, voxels_size)

    ref = numpy.array([[-4., -4., -4.],
                       [4., -4., -4.],
                       [-4., 4., -4.],
                       [-4., -4., 4.],
                       [4., 4., -4.],
                       [4., -4., 4.],
                       [-4., 4., 4.],
                       [4., 4., 4.]])

    assert numpy.array_equal(ref, res)

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
