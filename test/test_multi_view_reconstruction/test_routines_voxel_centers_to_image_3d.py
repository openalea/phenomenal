# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
from __future__ import division, print_function

import numpy

import openalea.phenomenal.object as phm_obj
# ==============================================================================


def test_simply_working_1():

    voxels_position = list()
    voxels_position.append((0, 0, 0))
    voxels_position.append((10, 10, 10))

    voxels_size = 2

    im = phm_obj.VoxelGrid(voxels_position, voxels_size).to_image_3d()

    assert im.ndim == 3

    xx, yy, zz = numpy.where(im == 1)

    assert len(xx) == 2

    assert max(xx) == 5
    assert min(xx) == 0


def test_simply_working_2():
    voxels_size = 16

    voxels_position = list()
    voxels_position.append((1, 42, 1))

    im = phm_obj.VoxelGrid(voxels_position, voxels_size).to_image_3d()

    assert im == [[[1]]]
    assert im.world_coordinate == (1, 42, 1)

    vpc = phm_obj.VoxelGrid.from_image_3d(im)

    assert len(vpc.voxels_position) == 1
    assert tuple(vpc.voxels_position[0]) == (1, 42, 1)
    assert vpc.voxels_size == 16


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
