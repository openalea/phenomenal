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
import collections

from alinea.phenomenal.multi_view_reconstruction import split_points_3d_plan
# ==============================================================================


def test_split_points_3d_plan_1():
    point_3d = (0.0, 0.0, 0.0)
    radius = 8

    points_3d = collections.deque()
    points_3d.append(point_3d)

    l = split_points_3d_plan(points_3d, radius)

    assert len(l) == 4
    assert l[0] == (0., -4., -4.)
    assert l[1] == (0., -4., 4.)
    assert l[2] == (0., 4., -4.)
    assert l[3] == (0., 4., 4.)

if __name__ == "__main__":
    test_split_points_3d_plan_1()
