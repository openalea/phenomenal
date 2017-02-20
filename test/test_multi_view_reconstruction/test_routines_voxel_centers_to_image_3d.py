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

from alinea.phenomenal.data_structure import (
    image_3d_to_voxels_position,
    voxels_position_to_image_3d)


# ==============================================================================


def test_simply_working_1():

    voxels_position = list()
    voxels_position.append((0, 0, 0))
    voxels_position.append((10, 10, 10))

    voxels_size = 2

    im = voxels_position_to_image_3d(voxels_position, voxels_size)

    assert im.ndim == 3

    xx, yy, zz = numpy.where(im == 1)

    assert len(xx) == 2

    assert max(xx) == 5
    assert min(xx) == 0


def test_simply_working_2():
    voxels_size = 16

    voxels_position = list()
    voxels_position.append((1, 42, 1))

    im = voxels_position_to_image_3d(voxels_position, voxels_size)

    assert im == [[[1]]]
    assert im.world_coordinate == (1, 42, 1)

    vcs, vs = image_3d_to_voxels_position(im)

    assert len(vcs) == 1
    assert vcs[0] == (1, 42, 1)
    assert vs == 16


if __name__ == "__main__":
    test_simply_working_1()
    test_simply_working_2()
