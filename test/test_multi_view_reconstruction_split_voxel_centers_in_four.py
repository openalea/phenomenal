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
import collections

from alinea.phenomenal.multi_view_reconstruction import (
    split_voxel_centers_in_four)
# ==============================================================================


def test_split_points_3d_plan_1():
    voxel_center = (0.0, 0.0, 0.0)
    voxel_size = 16

    voxel_centers = collections.deque()
    voxel_centers.append(voxel_center)

    l = split_voxel_centers_in_four(voxel_centers, voxel_size)

    assert len(l) == 4
    assert l[0] == (0., -4., -4.)
    assert l[1] == (0., -4., 4.)
    assert l[2] == (0., 4., -4.)
    assert l[3] == (0., 4., 4.)

if __name__ == "__main__":
    test_split_points_3d_plan_1()
