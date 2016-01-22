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
                                                 ModelProjection,
                                                 get_function_projection)

from alinea.phenomenal.multi_view_reconstruction import (
    get_bounding_box_voxel_projected)
# ==============================================================================


def test_bbox_projection_1():

    voxel_center = (0, 0, 0)
    voxel_size = 10

    projection = lambda pt: (pt[0], pt[1])

    res = get_bounding_box_voxel_projected(voxel_center, voxel_size, projection)
    x_min, x_max, y_min, y_max = res

    assert x_min == -10
    assert x_max == 10
    assert y_min == -10
    assert y_max == 10


def test_bbox_projection_2():
    params_camera_path, _ = plant_1_calibration_params_path()
    cam_params = CameraModelParameters.read(params_camera_path)

    angle = 0
    projection = get_function_projection(cam_params, angle)

    voxel_center = (0, 0, 0)
    voxel_size = 4

    res = get_bounding_box_voxel_projected(voxel_center, voxel_size, projection)

    assert res == (1016.657969220734,
                   1026.3381434879657,
                   1258.4181735951754,
                   1265.3138726030732)

if __name__ == "__main__":
    test_bbox_projection_1()
    test_bbox_projection_2()
