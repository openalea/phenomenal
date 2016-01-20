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
from alinea.phenomenal.plant_1 import plant_1_calibration_params_path
from alinea.phenomenal.calibration_model import (CameraModelParameters,
                                                 ModelProjection)

from alinea.phenomenal.multi_view_reconstruction import bbox_projection
# ==============================================================================


def test_bbox_projection_1():

    point_3d = (0, 0, 0)
    radius = 10

    class Projection(object):
        def __init__(self):
            self.project_point = lambda pt, angle: (pt[0], pt[1])

    projection = Projection()
    angle = 10

    res = bbox_projection(point_3d, radius, projection, angle)
    x_min, x_max, y_min, y_max = res

    assert x_min == -10
    assert x_max == 10
    assert y_min == -10
    assert y_max == 10


def test_bbox_projection_2():
    params_camera_path, _ = plant_1_calibration_params_path()
    cam_params = CameraModelParameters.read(params_camera_path)
    projection = ModelProjection(cam_params)

    point_3d = (0, 0, 0)
    radius = 4
    angle = 0

    res = bbox_projection(point_3d, radius, projection, angle)

    assert res == (1016.657969220734,
                   1026.3381434879657,
                   1258.4181735951754,
                   1265.3138726030732)

if __name__ == "__main__":
    test_bbox_projection_1()
    test_bbox_projection_2()
