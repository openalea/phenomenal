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
from math import cos, sin, radians

from alinea.phenomenal.frame import Frame, x_axis, y_axis, z_axis
from alinea.phenomenal.transformations import (
    concatenate_matrices, rotation_matrix)
# ==============================================================================


def rotation_point(x, y, z, degree):
    alpha = radians(degree)
    origin = [x * cos(alpha) - y * sin(alpha),
              x * sin(alpha) + y * cos(alpha),
              z]

    return origin


def compute_frame(origin, x_rotation, y_rotation, z_rotation):

    mat_rot_x = rotation_matrix(radians(x_rotation), x_axis)
    mat_rot_y = rotation_matrix(radians(y_rotation), y_axis)
    mat_rot_z = rotation_matrix(radians(z_rotation), z_axis)

    rot = concatenate_matrices(mat_rot_y, mat_rot_x, mat_rot_z)

    return Frame(rot[:3, :3].T, origin)

def test_chess_frame():

    origin_0 = rotation_point(100, 0, 50, 0)
    origin_90 = rotation_point(100, 0, 50, 90)
    print origin_0
    print origin_90
    print '\n ========================== \n'

    pt_110_0 = rotation_point(110, 0, 50, 0)
    pt_110_90 = rotation_point(110, 0, 50, 90)
    print pt_110_0
    print pt_110_90
    print '\n ========================== \n'

    f_0 = compute_frame(origin_0, 0, 0, 0)
    f_90 = compute_frame(origin_90, 0, 0, 90)
    f_900 = compute_frame(origin_90, 0, 0, -90)

    print 'Point Local :'
    print f_0.local_point(pt_110_0)
    print f_90.local_point(pt_110_90)
    print f_900.local_point(pt_110_90)

    print '\n ========================== \n'

    print f_0.global_point((10, 0, 0))
    print f_90.global_point((10, 0, 0))
    print f_900.global_point((10, 0, 0))


if __name__ == "__main__":
    test_chess_frame()
