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


from alinea.phenomenal.multi_view_reconstruction.multi_view_reconstruction\
    import (get_voxel_corners)
# ==============================================================================


def test_get_voxel_corners_1():
    voxel_center = (0.0, 0.0, 0.0)
    voxel_size = 16

    voxel_corners = get_voxel_corners(voxel_center, voxel_size / 2)

    assert len(voxel_corners) == 8

    assert voxel_corners[0] == (-4., -4., -4.)
    assert voxel_corners[1] == (4., -4., -4.)
    assert voxel_corners[2] == (-4., 4., -4.)
    assert voxel_corners[3] == (-4., -4., 4.)
    assert voxel_corners[4] == (4., 4., -4.)
    assert voxel_corners[5] == (4., -4., 4.)
    assert voxel_corners[6] == (-4., 4., 4.)
    assert voxel_corners[7] == (4., 4., 4.)

if __name__ == "__main__":
    test_get_voxel_corners_1()
