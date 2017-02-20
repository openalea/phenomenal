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

from alinea.phenomenal.data_structure import(
    Image3D,
    image_3d_to_voxels_position,
    voxels_position_to_image_3d)

# ==============================================================================


def test_simply_working_1():
    image_3d = Image3D.ones((10, 10, 10),
                            voxels_size=16,
                            dtype=numpy.uint8,
                            world_coordinate=(1, 2, 3))

    voxels_position, voxels_size = image_3d_to_voxels_position(image_3d)

    assert voxels_position[0] == (1., 2., 3.)
    assert voxels_position[1] == (1., 2., 19.)
    assert len(voxels_position) == image_3d.size


def test_simply_working_2():

    image_3d = Image3D.ones((10, 10, 10),
                            voxels_size=16,
                            dtype=numpy.uint8,
                            world_coordinate=(1, 2, 3))

    voxels_position, voxels_size = image_3d_to_voxels_position(image_3d)

    assert voxels_position[0] == (1., 2., 3.)
    assert voxels_position[1] == (1., 2., 19.)
    assert len(voxels_position) == image_3d.size

    im = voxels_position_to_image_3d(voxels_position, voxels_size)

    assert im.ndim == 3
    assert im.size == len(voxels_position)
    assert (im == image_3d).all()
    assert image_3d.world_coordinate == (1, 2, 3)


if __name__ == "__main__":
    test_simply_working_1()
    test_simply_working_2()
