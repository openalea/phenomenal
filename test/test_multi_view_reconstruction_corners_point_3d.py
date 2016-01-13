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


from alinea.phenomenal.multi_view_reconstruction import corners_point_3d
# ==============================================================================


def test_corners_point_3d_1():
    point_3d = (0.0, 0.0, 0.0)
    radius = 8

    points_3d = corners_point_3d(point_3d, radius / 2)

    assert len(points_3d) == 8

    assert points_3d[0] == (-4., -4., -4.)
    assert points_3d[1] == (4., -4., -4.)
    assert points_3d[2] == (-4., 4., -4.)
    assert points_3d[3] == (-4., -4., 4.)
    assert points_3d[4] == (4., 4., -4.)
    assert points_3d[5] == (4., -4., 4.)
    assert points_3d[6] == (-4., 4., 4.)
    assert points_3d[7] == (4., 4., 4.)

if __name__ == "__main__":
    test_corners_point_3d_1()
