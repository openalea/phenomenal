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

from alinea.phenomenal.multi_view_reconstruction.image3d import Image3D
from alinea.phenomenal.multi_view_reconstruction.routines import (
    image_3d_to_voxel_centers,
    voxel_centers_to_image_3d)


# ==============================================================================


def test_simply_working_1():
    image_3d = Image3D.ones((10, 10, 10),
                            voxel_size=16,
                            dtype=numpy.uint8,
                            world_coordinate=(1, 2, 3))

    voxel_centers, voxel_size = image_3d_to_voxel_centers(image_3d)

    assert voxel_centers[0] == (1., 2., 3.)
    assert voxel_centers[1] == (1., 2., 19.)
    assert len(voxel_centers) == image_3d.size


def test_simply_working_2():

    image_3d = Image3D.ones((10, 10, 10),
                            voxel_size=16,
                            dtype=numpy.uint8,
                            world_coordinate=(1, 2, 3))

    voxel_centers, voxel_size = image_3d_to_voxel_centers(image_3d)

    assert voxel_centers[0] == (1., 2., 3.)
    assert voxel_centers[1] == (1., 2., 19.)
    assert len(voxel_centers) == image_3d.size

    im = voxel_centers_to_image_3d(voxel_centers, voxel_size)

    assert im.ndim == 3
    assert im.size == len(voxel_centers)
    assert (im == image_3d).all()
    assert image_3d.world_coordinate == (1, 2, 3)


if __name__ == "__main__":
    test_simply_working_1()
    test_simply_working_2()
